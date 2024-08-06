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
import openai
from llama_index.core import VectorStoreIndex, Document, ServiceContext
from langchain_community.chat_models import ChatOpenAI

app = Flask(__name__)

# Initialize OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Flask-Caching
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)

@cache.memoize(timeout=300) #cache for 1 hour

def fetch_and_format_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()

        title = unescape(article.title)
        summary = unescape(article.summary)
        content = unescape(article.text)

        formatted_content = f"""
{title}

Quick Summary: {summary}

Content:
{content}
"""
        return formatted_content.strip()
    except Exception as e:
        print(f"Error fetching content: {e}")
        raise Exception("Failed to fetch and parse content")

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
    return render_template('index_2.6.html')

@app.route('/fetch', methods=['POST'])
@cache.cached(timeout=3600, key_prefix=lambda: request.json['url'])
def fetch_article():
    url = request.json['url']
    try:
        content = fetch_and_format_content(url)
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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