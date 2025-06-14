# 📚 Reader App

The Reader App is a web application that allows users to fetch articles from a given URL, view the content, generate a PDF version of the article, and query the article using natural language processing techniques.

## Features

- 📰 Article Fetching: Extract content from any web URL using Firecrawl
- 📝 Automatic Summarization: Generate concise summaries using GPT models
- 🔍 Interactive Querying: Ask questions about the article using various LLM models
- 📄 PDF Generation: Download articles as beautifully formatted PDFs
- 🎨 Multiple Themes: Support for light, dark, and sepia themes
- 💡 Smart Highlighting: Highlight relevant parts of the article during Q&A
- 🔐 Server-side API Keys: No need for users to provide their own API keys

## Available Models

- OpenAI Models:
  - GPT-4o Mini (Default - Cost Effective)
  - GPT-3.5 Turbo
  - GPT-4o
- Llama Models:
  - Llama 3.1 (70B)
  - Gemma 2 (27B)
  - Mistral Large (Mixtral-8x7B)
  - Qwen 2 (72B)

## Project Structure

```
Reader/
├── app.py                 # Main Flask application
├── static/               # Static assets
│   ├── chat.js          # Chat functionality
│   ├── news.js          # News-related features
│   ├── styles.css       # Main styles
│   ├── tailwind.css     # Tailwind styles
│   ├── themes.js        # Theme switching
│   └── utils.js         # Utility functions
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Main page
│   └── navbar.html     # Navigation
└── utils/              # Python utilities
    ├── constants.py    # Constants and enums
    ├── fetch/         # URL fetching utilities
    ├── generate/      # PDF generation
    └── index/         # Search indexing
```

## Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

**Server-side API Keys Required:**
- OpenAI API key (for GPT models and summarization)
- Firecrawl API key (for web scraping)
- (Optional) Llama API key for additional models

### Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/Reader.git
   cd Reader
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a .env file with your API keys:
   ```sh
   # Server-side API keys - Required for the application to function
   # Users do not need to provide their own API keys

   # OpenAI API key for GPT models and article summarization
   OPENAI_API_KEY='your_openai_api_key_here'

   # Firecrawl API key for web scraping
   FIRECRAWL_API_KEY='your_firecrawl_api_key_here'

   # Optional: Llama API key for non-OpenAI models (Llama, Gemma, Mistral, Qwen)
   LLAMA_API_KEY='your_llama_api_key_here'
   ```

5. Run the application:
   ```sh
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:8080`

## Dependency Management

The project has undergone a significant dependency reduction to streamline the application and reduce its footprint. The following changes were made:

- **Removed `langchain`**: The project now exclusively uses `llama-index` for all RAG (Retrieval-Augmented Generation) functionalities, removing the redundancy of having two similar frameworks.
- **Removed `pandas` and `newspaper3k`**: These heavy libraries were removed to reduce the overall size of the application.
- **Replaced `scikit-learn`**: The `cosine_similarity` function from `scikit-learn` was replaced with a more lightweight implementation using `numpy`.
- **Removed Redundant HTTP Libraries**: The project now standardizes on the `requests` library for HTTP requests, removing `httpx` and `aiohttp`.
- **Removed Unused Utilities**: Various other unused utility libraries were removed to further clean up the dependencies.

This has resulted in a much smaller and more manageable `requirements.txt` file.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| OPENAI_API_KEY | Yes | Your OpenAI API key for GPT models and summarization |
| FIRECRAWL_API_KEY | Yes | Your Firecrawl API key for web scraping |
| LLAMA_API_KEY | No | Your Llama API key for additional models |
| FLASK_ENV | No | Set to 'development' for debug mode |
| PORT | No | Custom port (default: 8080) |

## API Documentation

### /fetch (POST)
Fetches and processes an article from a URL.
- Request body: `{ "url": "article_url" }`
- Response: `{ "content": { "title", "content", "top_image_url", "markdown_content" }, "summary" }`

### /query (POST)
Queries an article using natural language.
- Request body: `{ "content": "article_content", "query": "your_question", "model": "model_name" }`
- Response: `{ "result": "answer" }`

### /generate_pdf (POST)
Generates a PDF version of the article.
- Request body: `{ "title": "article_title", "content": "article_content", "imageUrl": "top_image_url" }`
- Response: PDF file

## Troubleshooting

### Common Issues

1. **"Unable to fetch article"**
   - Check if the website allows web scraping
   - Try using a different URL from the same source
   - Ensure you're not being rate-limited
   - Verify your Firecrawl API key is valid

2. **"OpenAI API Error"**
   - Verify your API key is correct
   - Check your API usage limits
   - Ensure your request isn't too long

3. **"Firecrawl API Error"**
   - Verify your Firecrawl API key is valid
   - Check your Firecrawl usage limits
   - Ensure the URL is accessible

4. **PDF Generation Fails**
   - Check if the article content is not empty
   - Verify the image URL is accessible
   - Ensure you have sufficient permissions

### Development Tips

- Enable debug mode for detailed error messages
- Use the browser console to check for JavaScript errors
- Monitor the Flask server logs for backend issues
- Check the network tab for API response details

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Acknowledgements

This app was developed as part of the Stanford Continuing Studies class TECH-16: LLMs for Business with Python taught by Charlie Flanagan. The app owes its thanks to him, Dima Timofeev, and many others including the teams who built the app's various dependencies.

## License

This project is open-source and available under the [Apache License 2.0](LICENSE).
