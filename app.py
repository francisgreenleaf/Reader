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
    session,
)
from flask_caching import Cache
from flask_session import Session  # Add this import for session management
from newspaper import Article, ArticleException, Config

from utils.constants import IndexModel
from utils.fetch import imageUtils
from utils.generate import pdfUtils
from utils.index import indexUtils
from utils.tokenguard import tokenguard

handler = colorlog.StreamHandler()

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
# Raise an error if the API key is not set
if openai.api_key is None:
    raise ValueError("OpenAI API Key is not set. Please set it in the .env file.")

# Initialize Flask-Caching
app.config["CACHE_TYPE"] = "SimpleCache"
cache = Cache(app)

# Configure session for Flask app
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the file system
Session(app)  # Initialize the session extension

@dataclass
class FormattedContent:
    title: str
    summary: str
    content: str
    top_image_url: str


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
    top_image_url = article.top_image if (imageUtils.is_image_displayed(article.top_image, article.html)) else ''

    return FormattedContent(
        title=title, summary=summary, content=content, top_image_url=top_image_url
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
    pdf = pdfUtils.generate_pdf(content)
    pdf.seek(0)
    sanitized_title = "".join(c if c.isalnum() else "_" for c in title)
    return send_file(
        pdf,
        download_name=f"{sanitized_title}.pdf",
        as_attachment=True,
        mimetype="application/pdf",
    )


@app.route("/query", methods=["POST"])
# This is where tokenguard should be initialized
def query_article():
    content = request.json["content"]
    query = request.json["query"]
    model = request.json.get("model", "gpt-4o-mini")  # default
    indexModel = IndexModel.VECTOR_STORE
    temperature = 0.0

    try:
        # Initialize or retrieve the RAG index from session
        if 'index_abc' not in session:
            # Create the RAG index
            print("Initialize a session index")
            index = indexUtils.create_rag_index(content, model, indexModel)(content, model, temperature)
            session['index_abc'] = index
            session['chat_history'] = []
        else:
            print("Reuse a session index")
            index = session['index_abc']

        # Create the chat engine
        query_engine = index.as_chat_engine(chat_mode='openai', verbose=True)
        
        # Append previous chat history if any
        for msg in session['chat_history']:
            query_engine.chat_history.append(msg)
        print("History: ", query_engine.chat_history)
        ## Need to discuss with team!!
        query = "History: " + str(query_engine.chat_history) + '\n\n' + query
        print("Query: ", query)

        # Use RAG to get relevant content
        suffix = "\n\nPlease make sure the output is well formatted. For example, add bold on numbers or bullet points if necessary."
        response = query_engine.query(query + suffix)
        session['chat_history'].append({"query": query, "response": str(response)})

        return jsonify({"result": str(response)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/clear_history", methods=["POST"])
def clear_history():
    session.pop('index', None)
    session.pop('chat_history', None)
    return jsonify({"status": "Chat history cleared"})


if __name__ == "__main__":
    app.run(port=8080, debug=True)
