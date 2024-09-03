import os
import nltk
from dataclasses import dataclass
from html import unescape
import colorlog
import openai
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_caching import Cache
from flask_limiter import Limiter
from newspaper import Article, ArticleException, Config
from utils.fetch import imageUtils
from utils.generate import pdfUtils
from openai import OpenAI

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

# Load environment variables at the beginning
load_dotenv()

#initialize Flask
app = Flask(__name__)

# Initialize Flask-Caching
app.config["CACHE_TYPE"] = "SimpleCache"
cache = Cache(app)

# TODO: Initialize rate limiter
#imiter = Limiter(
   # get_remote_address,
    #app=app,
    #default_limits=["200 per day", "50 per hour"],
    #storage_uri="memory://localhost:5050"
#)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key is not set. Please set it in the .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


@dataclass
class FormattedContent:
    title: str
    content: str
    top_image_url: str

def generate_summary(content):
    # TODO: add OpenAI API Key as ARG
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # TODO: add model from Front
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Summarize the following article in a concise paragraph:\n\"\"\"{content}\"\"\""}
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

    # Configure newspaper
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
def fetch_article():
    url = request.json.get("url")
    if not url:
        return handle_error("Missing URL", 400)
    
    try:
        content = fetch_and_format_content(url)
        if not content.title or not content.content:
            raise ValueError("Failed to extract meaningful content from the URL")
        
        summary = generate_summary(content.content)
        
        return jsonify({"content": content.__dict__, "summary": summary})
    except Exception as e:
        return handle_error(f"Error fetching article: {str(e)}")
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
def query_article():
    logger.info("Received query request")
    content = request.json.get("content")
    query = request.json.get("query")

    logger.info(f"Content length: {len(content) if content else 'None'}, Query: {query}")

    if not all([content, query]):
        logger.error("Missing required fields in request")
        return jsonify({"error": "Missing required fields"}), 400

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return jsonify({"error": "OpenAI API key not configured"}), 500

    client = OpenAI(api_key=api_key)

    try:
        # First, check if the query is related to the article
        relevance_check = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that determines if a question is related to a given article."},
                {"role": "user", "content": f"Article content: {content[:500]}...\n\nQuestion: {query}\n\nIs this question related to the article? Answer with 'Yes' or 'No' only."}
            ],
            max_tokens=10
        )
        is_relevant = relevance_check.choices[0].message.content.strip().lower() == "yes"

        if is_relevant:
            # If the query is relevant, proceed with answering it
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions about articles."},
                    {"role": "user", "content": f"Article content: {content}\n\nQuestion: {query}"}
                ],
                max_tokens=500
            )
            answer = response.choices[0].message.content.strip()
        else:
            # If the query is not relevant, provide a polite response
            answer = (
                "I apologize, but your question doesn't seem to be related to the article we're discussing. "
                "Would you like to ask something about the content of the article instead? "
                "I'd be happy to help you understand or analyze any part of the article."
            )

        logger.info("Successfully generated response")
        return jsonify({"result": answer})
    except Exception as e:
        error_message = f"Error processing query: {str(e)}"
        logger.error(error_message)
        return jsonify({"error": error_message}), 500


def handle_error(error_message, status_code=500):
    logger.error(error_message)
    return jsonify({"error": error_message}), status_code


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429


if __name__ == "__main__":
    app.run(port=5000, debug=True)
