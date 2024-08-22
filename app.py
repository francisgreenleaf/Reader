import os
from dataclasses import dataclass
from html import unescape
import colorlog
import openai
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    send_from_directory,
)
from flask_caching import Cache
from newspaper import Article, ArticleException, Config

from utils.constants import IndexModel
from utils.fetch import imageUtils
from utils.generate import pdfUtils
from utils.index import indexUtils
from utils.tokenguard import tokenguard
from openai import OpenAI

handler = colorlog.StreamHandler()

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
#Raise an error if the API key is not set
if openai.api_key is None:
    raise ValueError("OpenAI API Key is not set. Please set it in the .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#Raise an error if the API key is not set
if client.api_key is None:
    raise ValueError("OpenAI API Key is not set. Please set it in the .env file.")

# Initialize Flask-Caching
app.config["CACHE_TYPE"] = "SimpleCache"
cache = Cache(app)

@dataclass
class FormattedContent:
    title: str
    content: str
    top_image_url: str

def generate_summary(content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Summarize the following article in a concise paragraph:\n\n{content}"}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Unable to generate summary."

@cache.memoize(timeout=300)  # cache for 5 minutes
def fetch_and_format_content(url):
    logger.info(f"Fetching content from URL: {url}")

    #Configure newspaper
    config = Config()
    config.fetch_images = True
    config.memoize_articles = False

    article = Article(url, config=config)

    try:
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
    top_image_url = article.top_image if (imageUtils.is_image_displayed(article.top_image, article.html)) else ''

    return FormattedContent(
        title=title, content=content, top_image_url=top_image_url
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/public/<path:filename>")
def public_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route("/fetch", methods=["POST"])
def fetch_article():
    url = request.json["url"]
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
def generate_pdf_route():
    data = request.json
    title = data.get("title", "article")
    content = data.get("content", "")
    top_image_url = data.get("imageUrl", "")
    pdf = pdfUtils.generate_pdf(content, top_image_url)
    pdf.seek(0)
    sanitized_title = "".join(c if c.isalnum() else "_" for c in title)
    return send_file(
        pdf,
        download_name=f"{sanitized_title}.pdf",
        as_attachment=True,
        mimetype="application/pdf",
    )


@app.route("/query", methods=["POST"])
#this is where tokenguard should be initialized - currently it is not being used
def query_article():
    content = request.json["content"]
    query = request.json["query"]
    model = request.json.get(
        "model", "gpt-4o-mini" # default
    )
    api_key = request.json.get("apiKey")
    #use the provided API key if it is set, otherwise use the default key
    if api_key:
        openai.api_key = api_key
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")#this is the default key set in the .env file - when this app is deployed, the user provides their own key via the settings page. 

    indexModel = IndexModel.VECTOR_STORE
    temperature = 0.0

    try:
        # Create RAG index
        index = indexUtils.create_rag_index(content, model, indexModel)(content, model, temperature)
        query_engine = index.as_query_engine()
        # Use RAG to get relevant content
        response = query_engine.query(query)
        relevant_content = str(response)

        return jsonify({"result": str(response)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

if __name__ == "__main__":
    app.run(port=8080, debug=True)
