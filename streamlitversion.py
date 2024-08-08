import streamlit as st
from newspaper import Article
from html import unescape
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch
import openai
from llama_index.core import VectorStoreIndex, Document, ServiceContext
from langchain_community.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set page config for dark theme
st.set_page_config(page_title="Reader", page_icon="📚", layout="centered", initial_sidebar_state="expanded")

# Apply dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #e2e8f0;
    }
    .stTextInput > div > div > input {
        background-color: #1e1e1e;
        color: white;
    }
    .stButton > button {
        background-color: #3b82f6;
        color: white;
    }
    .stTextArea > div > div > textarea {
        background-color: #252526;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def fetch_and_format_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()

        title = unescape(article.title)
        summary = unescape(article.summary)
        content = unescape(article.text)

        return {
            "title": title,
            "summary": summary,
            "content": content
        }
    except Exception as e:
        st.error(f"Error fetching content: {str(e)}")
        return None

def generate_pdf(content):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    flowables = []

    # Add title
    flowables.append(Paragraph(content['title'], styles['Heading1']))
    flowables.append(Spacer(1, 12))

    # Add summary
    flowables.append(Paragraph("Summary:", styles['Heading2']))
    flowables.append(Paragraph(content['summary'], styles['Justify']))
    flowables.append(Spacer(1, 12))

    # Add content
    flowables.append(Paragraph("Content:", styles['Heading2']))
    for line in content['content'].split('\n'):
        if line.strip():
            p = Paragraph(line, styles['Justify'])
            flowables.append(p)
        else:
            flowables.append(Spacer(1, 6))

    doc.build(flowables)
    buffer.seek(0)
    return buffer

def create_rag_index(content):
    document = Document(text=content)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    service_context = ServiceContext.from_defaults(llm=llm)
    index = VectorStoreIndex.from_documents([document], service_context=service_context)
    return index

st.title("📚 Reader")

url = st.text_input("Enter article URL")

if st.button("Fetch Article"):
    if url:
        with st.spinner("Fetching article..."):
            article_content = fetch_and_format_content(url)
        
        if article_content:
            st.subheader(article_content['title'])
            st.write("**Summary:**")
            st.write(article_content['summary'])
            st.write("**Content:**")
            st.write(article_content['content'])

            # Store the content in session state for later use
            st.session_state.article_content = article_content

            # PDF Generation
            pdf_buffer = generate_pdf(article_content)
            st.download_button(
                label="Download as PDF",
                data=pdf_buffer,
                file_name="article.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Please enter a URL")

# Query functionality
st.subheader("Query the Article")
query = st.text_input("Enter your query")

if st.button("Submit Query"):
    if 'article_content' in st.session_state and query:
        with st.spinner("Processing query..."):
            content = st.session_state.article_content['content']
            index = create_rag_index(content)
            query_engine = index.as_query_engine()
            response = query_engine.query(query)
            st.write("**Query Result:**")
            st.write(str(response))
    elif not 'article_content' in st.session_state:
        st.warning("Please fetch an article first")
    else:
        st.warning("Please enter a query")

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)