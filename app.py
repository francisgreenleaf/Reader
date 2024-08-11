import os
from dataclasses import dataclass, field
from html import unescape
from typing import List

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

# Initialize Flask-Caching
app.config["CACHE_TYPE"] = "SimpleCache"
cache = Cache(app)


@dataclass
class FormattedContent:
    title: str
    summary: str
    content: str
    images: List = field(default_factory=list)


@cache.memoize(timeout=300)  # cache for 5 minutes
#fetch and format content function is no longer one large try except block 
#but instead has individual try except blocks for specific exceptions
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
        article.nlp()

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
    summary = unescape(article.summary)
    content = unescape(article.text)

    images = imageUtils.fetch_images(article.images, requests, logger)

    logger.info(f"Successfully parsed article. Title: {title}")
    logger.info(f"Number of images found: {len(images)}")

    return FormattedContent(
        title=title, summary=summary, content=content, images=images
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
        return jsonify({"content": content})
    except Exception as e:
        error_message = f"Error fetching article: {str(e)}"
        logger.error(error_message, exc_info=True)
        return jsonify({"error": error_message}), 400


@app.route("/generate_pdf", methods=["POST"])
def generate_pdf_route():
    data = request.json
    title = data.get("title", "article")
    content = data.get("content", "")
    images = data.get("images", [])
    pdf = pdfUtils.generate_pdf(content, images)
    pdf.seek(0)
    sanitized_title = "".join(c if c.isalnum() else "_" for c in title)
    return send_file(
        pdf,
        download_name=f"{sanitized_title}.pdf",
        as_attachment=True,
        mimetype="application/pdf",
    )


@app.route("/query", methods=["POST"])
def query_article():
    content = request.json["content"]
    query = request.json["query"]
    model = request.json.get(
        "model", "gpt-4o-mini" # default
    )
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
