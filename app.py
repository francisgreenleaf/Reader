import os
import re
import time
import random
import logging
from dataclasses import dataclass
from functools import wraps
from html import unescape
from urllib.parse import urlparse

# Third-party imports
import nltk
import colorlog
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    send_from_directory,
    current_app,
)
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from llamaapi import LlamaAPI
from newspaper import Article, ArticleException, Config
from openai import OpenAI, OpenAIError

# Local imports

from utils.constants import IndexModel
from utils.fetch import imageUtils
from utils.generate import pdfUtils
from utils.index import indexUtils
from utils.tokenguard import tokenguard

MODELS = {
    "llama-3.1": "llama3.1-70b",
    "gemma-2": "gemma2-27b",
    "mistral-large": "mixtral-8x7b-instruct",
    "qwen-2": "Qwen2-72B",
}

handler = colorlog.StreamHandler()

nltk.download('punkt')

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if client.api_key is None:
    raise ValueError("OpenAI API Key is not set. Please set it in the .env file.")

# Enhanced caching configuration
cache_config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes default
    "CACHE_THRESHOLD": 1000,  # Maximum number of items the cache will store
}
app.config.update(cache_config)
cache = Cache(app)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    """
    Decorator that implements an exponential backoff retry strategy
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, OpenAIError) as e:
                    if x == retries:
                        raise
                    else:
                        sleep = (backoff_in_seconds * 2 ** x +
                               random.uniform(0, 1))
                        time.sleep(sleep)
                        x += 1
        return wrapper
    return decorator

def validate_url(url):
    """
    Validate URL format and scheme
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def validate_content(content):
    """
    Validate that content is non-empty and within reasonable size limits
    """
    if not content or not isinstance(content, str):
        return False
    # Limit content to 100KB
    return len(content.encode('utf-8')) <= 100 * 1024

def validate_api_key(api_key):
    """
    Validate API key format
    """
    if not api_key:
        return True  # Allow empty for default key
    # Basic format check for OpenAI and Llama API keys
    return bool(re.match(r'^[a-zA-Z0-9_-]{20,}$', api_key))

def handle_timeout(func):
    """
    Decorator to handle request timeouts
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            return jsonify({
                "error": "Request timed out. Please try again."
            }), 408
        except requests.exceptions.ConnectionError:
            return jsonify({
                "error": "Connection error. Please check your internet connection."
            }), 503
    return wrapper

@dataclass
class FormattedContent:
    title: str
    content: str
    top_image_url: str

def generate_summary(content):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Using a stable model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Summarize the following article in a concise paragraph:\n\"\"\"{content}\"\"\""}
            ],
            max_tokens=500,
            timeout=15  # 15 second timeout for summary generation
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return f"Error generating summary: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error generating summary: {str(e)}")
        return "An unexpected error occurred while generating the summary."

@cache.memoize(timeout=3600)  # cache for 1 hour
@retry_with_backoff()
@handle_timeout
def fetch_and_format_content(url):
    logger.info(f"Fetching content from URL: {url}")

    # Configure newspaper
    config = Config()
    config.fetch_images = True
    config.memoize_articles = False

    article = Article(url, config=config)

    try:
        # Configure requests session with timeout
        session = requests.Session()
        session.timeout = 10  # 10 seconds timeout
        article.session = session
        
        article.download()
        article.parse()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.error(f"403 Forbidden error when accessing {url}")
            raise ValueError(f"Access to the content at {url} is forbidden. The website may be blocking automated access or requiring authentication.")
    except ArticleException as e:
        logger.error(f"Error fetching article: {e}")
        raise ValueError(f"Failed to parse article from {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching article: {e}")
        raise ValueError(f"An unexpected error occurred while fetching the article from {url}: {str(e)}")

    title = unescape(article.title)
    content = unescape(article.text)
    # TODO: Fix the call 'imageUtils.is_image_displayed' not geting the image url
    top_image_url = article.top_image if (imageUtils.is_image_displayed(article.top_image, article.html)) else ''

    return FormattedContent(
        title=title, content=content, top_image_url=article.top_image
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/public/<path:filename>")
def public_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route("/fetch", methods=["POST"])
@limiter.limit("30 per minute")  # Rate limit for article fetching
@handle_timeout
def fetch_article():
    url = request.json.get("url")
    if not url or not validate_url(url):
        return jsonify({"error": "Invalid or missing URL"}), 400
    try:
        content = fetch_and_format_content(url)
        if not content.title or not content.content:
            raise ValueError("Failed to extract meaningful content from the URL")
        
        summary = generate_summary(content.content)
        
        return jsonify({"content": content.__dict__, "summary": summary})
    except Exception as e:
        error_message = f"Error fetching article: {str(e)}"
        logger.error(error_message, exc_info=True)
        return jsonify({"error": error_message}), 400


@app.route("/generate_pdf", methods=["POST"])
@limiter.limit("10 per minute")  # Rate limit for PDF generation
@handle_timeout
def generate_pdf_route():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        title = data.get("title", "article")
        content = data.get("content", "")
        
        if not validate_content(content):
            return jsonify({"error": "Invalid or missing content"}), 400
            
        if not isinstance(title, str) or len(title) > 200:  # Reasonable title length limit
            return jsonify({"error": "Invalid title"}), 400
            
        top_image_url = data.get("imageUrl", "")
        sanitized_title = "".join(c if c.isalnum() else "_" for c in title)
        
        # Generate cache key based on content hash
        cache_key = f"pdf_{hash(content)}"
        
        # Try to get PDF from cache
        cached_pdf = cache.get(cache_key)
        if cached_pdf:
            logger.info(f"Serving cached PDF for {sanitized_title}")
            return send_file(
                cached_pdf,
                download_name=f"{sanitized_title}.pdf",
                as_attachment=True,
                mimetype="application/pdf",
            )
        
        # Generate new PDF if not in cache
        logger.info(f"Generating new PDF for {sanitized_title}")
        pdf = pdfUtils.generate_pdf(content, top_image_url)
        pdf.seek(0)
        
        # Cache the PDF for 1 hour
        cache.set(cache_key, pdf, timeout=3600)
        
        return send_file(
            pdf,
            download_name=f"{sanitized_title}.pdf",
            as_attachment=True,
            mimetype="application/pdf",
        )
    except Exception as e:
        error_message = f"Error generating PDF: {str(e)}"
        logger.error(error_message, exc_info=True)
        return jsonify({"error": error_message}), 500


@app.route("/query", methods=["POST"])
@limiter.limit("20 per minute")  # Rate limit for queries
@handle_timeout
# this is where tokenguard should be initialized - currently it is not being used
def query_article():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    model = data.get("model")
    api_key = data.get("apiKey")
    content = data.get("content")
    query = data.get("query")
    
    # Validate inputs
    if not model or model not in MODELS and model not in ["gpt-4-turbo-preview", "gpt-3.5-turbo", "gpt-4"]:
        return jsonify({"error": "Invalid or unsupported model"}), 400
        
    if api_key and not validate_api_key(api_key):
        return jsonify({"error": "Invalid API key format"}), 400
        
    if not validate_content(content):
        return jsonify({"error": "Invalid or missing content"}), 400
        
    if not query or not isinstance(query, str) or len(query) > 1000:  # Reasonable query length limit
        return jsonify({"error": "Invalid or missing query"}), 400
    if model in ["gpt-4-turbo-preview", "gpt-3.5-turbo", "gpt-4"]:
        try:
            # Create a new OpenAI client with the provided API key or use the default one
            openai_client = OpenAI(api_key=api_key) if api_key else client
            indexModel = IndexModel.VECTOR_STORE
            temperature = 0.2

            prompt = f"""
                You need to write your answer into the MarkDown format.
                You can link and highlight part of the article using MarkDown link like so: \"\"\"[Source](#highlight=Exact%20Text%20from%20the%20content)\"\"\",
                Do not use '-' for space use '%20' instead, and refer to the content using the exact words within the content.
                Do not hesitate to link and highlight each part of the content that informs your answer.
                This is the content: <content>{content}</content>
                """

            # Create RAG index
            index = indexUtils.create_rag_index(prompt, model, indexModel)
            if index is None:
                raise ValueError("Failed to create RAG index")
            
            query_engine = index.as_query_engine()
            # Use RAG to get relevant content
            response = query_engine.query(query)

            return jsonify({"result": str(response)})
        except OpenAIError as e:
            logger.error(f"OpenAI API Error in query: {str(e)}")
            return jsonify({"error": f"OpenAI API Error: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Unexpected error in query: {str(e)}")
            return jsonify({"error": str(e)}), 400
    else:
        api_key = api_key if api_key else os.getenv("LLAMA_API_KEY")
        llama = LlamaAPI(api_key)
        try:
            api_request_json = {
                "model": MODELS[model],
                "messages": [
                    {"role": "system", "content": query},
                    {"role": "user", "content": content},
                ],
                "timeout": 15  # 15 second timeout for LLM queries
            }
            # Make your request and handle the response
            response = llama.run(api_request_json)
            return jsonify({"result": response.json()["choices"][0]["message"]["content"]})
        except Exception as e:
            return jsonify({"error": str(e)}), 400      
    

if __name__ == "__main__":
    # Configure logging
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Reader startup')
    
    app.run(port=8080, debug=True)
