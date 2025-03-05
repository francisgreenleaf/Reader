import os
import nltk
from dataclasses import dataclass
from html import unescape
import colorlog
import requests
from llamaapi import LlamaAPI
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
from openai import OpenAI, OpenAIError

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
            model="gpt-4-turbo-preview",  # Using a stable model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Summarize the following article in a concise paragraph:\n\"\"\"{content}\"\"\""}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return f"Error generating summary: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error generating summary: {str(e)}")
        return "An unexpected error occurred while generating the summary."

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
# this is where tokenguard should be initialized - currently it is not being used
def query_article():
    # the user must input an API key
    model = request.json.get("model")
    api_key = request.json.get("apiKey")
    
    content = request.json["content"]
    query = request.json["query"]
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
                ]
            }
            # Make your request and handle the response
            response = llama.run(api_request_json)
            return jsonify({"result": response.json()["choices"][0]["message"]["content"]})
        except Exception as e:
            return jsonify({"error": str(e)}), 400      
    

if __name__ == "__main__":
    app.run(port=8080, debug=True)
