from flask import Flask, render_template, request, jsonify, send_file
from flask_caching import Cache
from newspaper import Article, Config
from html import unescape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
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
import requests
import base64
from PIL import Image
from io import BytesIO

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

@cache.memoize(timeout=300) # cache for 5 minutes
def fetch_and_format_content(url):
    try:
        logger.info(f"Fetching content from URL: {url}")
        
        # Configure newspaper
        config = Config()
        config.fetch_images = True
        config.memoize_articles = False
        
        article = Article(url, config=config)
        article.download()
        article.parse()
        article.nlp()

        title = unescape(article.title)
        summary = unescape(article.summary)
        content = unescape(article.text)

        # Fetch images
        images = []
        for img in article.images:
            try:
                # Skip SVG images
                if img.lower().endswith('.svg'):
                    logger.info(f"Skipping SVG image: {img}")
                    continue
                
                logger.info(f"Attempting to fetch image: {img}")
                response = requests.get(img, timeout=10)
                if response.status_code == 200:
                    img_data = base64.b64encode(response.content).decode('utf-8')
                    images.append({
                        'src': img,
                        'data': img_data
                    })
                    logger.info(f"Successfully fetched image: {img}")
                else:
                    logger.warning(f"Failed to fetch image: {img}. Status code: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching image {img}: {e}", exc_info=True)

        logger.info(f"Successfully parsed article. Title: {title}")
        logger.info(f"Number of images found: {len(images)}")

        formatted_content = {
            "title": title,
            "summary": summary,
            "content": content,
            "images": images
        }

        return formatted_content
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {e}", exc_info=True)
        raise

def generate_pdf(content, images):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    flowables = []

    # Add title
    title = content.split('\n')[0]
    flowables.append(Paragraph(title, styles['Heading1']))
    flowables.append(Spacer(1, 12))

    # Add content and images
    content_lines = content.split('\n')[1:]
    for i, line in enumerate(content_lines):
        if line.strip():
            p = Paragraph(line, styles['Justify'])
            flowables.append(p)
        else:
            flowables.append(Spacer(1, 6))
        
        # Add an image after every 5 paragraphs, if available
        if i % 5 == 0 and images:
            img_data = base64.b64decode(images[0]['data'])
            img = Image.open(BytesIO(img_data))
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            img_width = 6 * inch
            img_height = aspect * img_width
            flowables.append(ReportLabImage(BytesIO(img_data), width=img_width, height=img_height))
            flowables.append(Spacer(1, 12))
            images.pop(0)

    doc.build(flowables)
    buffer.seek(0)
    return buffer

def create_rag_index(content, model):
    # Create a Document object from the content
    document = Document(text=content)

    # Create service context with selected model
    llm = ChatOpenAI(model_name=model, temperature=0)
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
    data = request.json
    title = data.get('title', 'article')
    content = data.get('content', '')
    images = data.get('images', [])
    pdf = generate_pdf(content, images)
    pdf.seek(0)
    sanitized_title = ''.join(c if c.isalnum() else '_' for c in title)
    return send_file(pdf, download_name=f'{sanitized_title}.pdf', as_attachment=True, mimetype='application/pdf')

@app.route('/query', methods=['POST'])
def query_article():
    content = request.json['content']
    query = request.json['query']
    model = request.json.get('model', 'gpt-3.5-turbo')  # Default to gpt-3.5-turbo if no model is specified

    try:
        index = create_rag_index(content, model)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return jsonify({"result": str(response)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=8080, debug=True)
