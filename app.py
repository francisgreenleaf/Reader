from flask import Flask, render_template, request, jsonify, send_file
from flask_caching import Cache
from newspaper import Article
from html import unescape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch
import io
import os
from dotenv import load_dotenv
import openai
from llama_index.core import VectorStoreIndex, Document, ServiceContext
from langchain_community.chat_models import ChatOpenAI
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Flask-Caching
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@cache.memoize(timeout=300) #cache for 1 hour

def fetch_and_format_content(url):
    try:
        logger.info(f"Fetching content from URL: {url}")
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()

        title = unescape(article.title)
        summary = unescape(article.summary)
        content = unescape(article.text)

        logger.info(f"Successfully parsed article. Title: {title}")

        formatted_content = {
            "title": title,
            "summary": summary,
            "content": content
        }

        return formatted_content
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {e}", exc_info=True)
        raise

def generate_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    flowables = []

    #add title
    title = content.split('\n')[0]
    flowables.append(Paragraph(title, styles['Heading1']))
    flowables.append(Spacer(1,12))

    #add content
    for line in content.split('\n')[1:]:
        if line.strip():
            p = Paragraph(line, styles['Justify'])
            flowables.append(p)
        else:
            flowables.append(Spacer(1,6))

    doc.build(flowables)
    buffer.seek(0)
    return buffer

def create_rag_index(content):
    # Create a Document object from the content
    document = Document(text=content)

    # Create service context with ChatOpenAI
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    service_context = ServiceContext.from_defaults(llm=llm)

    # Create index
    index = VectorStoreIndex.from_documents(
        [document], 
        service_context=service_context
    )

    return index

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch_article():
    url = request.json['url']
    try:
        # Use the cached function directly
        content = fetch_and_format_content(url)
        if not content['title'] or not content['content']:
            raise ValueError("Failed to extract meaningful content from the URL")
        return jsonify({"content": content})
    except Exception as e:
        error_message = f"Error fetching article: {str(e)}"
        logger.error(error_message, exc_info=True)
        return jsonify({"error": error_message}), 400

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf_route():
    content = request.json['content']
    pdf = generate_pdf(content)
    return send_file(pdf, download_name='article.pdf', as_attachment=True, mimetype='application/pdf')

@app.route('/query', methods=['POST'])
def query_article():
    content = request.json['content']
    query = request.json['query']
    
    try:
        index = create_rag_index(content)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return jsonify({"result": str(response)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=8080,debug=True)