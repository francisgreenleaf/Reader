# 📚 Reader App

The Reader App is a web application that allows users to fetch articles from a given URL, view the content, generate a PDF version of the article, and query the article using natural language processing techniques.

## Features

- 📰 Article Fetching: Extract content from any web URL
- 📝 Automatic Summarization: Generate concise summaries using GPT models
- 🔍 Interactive Querying: Ask questions about the article using various LLM models
- 📄 PDF Generation: Download articles as beautifully formatted PDFs
- 🎨 Multiple Themes: Support for light, dark, and sepia themes
- 💡 Smart Highlighting: Highlight relevant parts of the article during Q&A

## Available Models

- OpenAI Models:
  - GPT-4 Turbo Preview
  - GPT-3.5 Turbo
  - GPT-4
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
│   ├── script.js        # Core JavaScript
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
    ├── index/         # Search indexing
    └── tokenguard/    # Token management
```

## Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- OpenAI API key
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
   OPENAI_API_KEY=your_openai_key_here
   LLAMA_API_KEY=your_llama_key_here  # Optional
   ```

5. Run the application:
   ```sh
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:8080`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| OPENAI_API_KEY | Yes | Your OpenAI API key |
| LLAMA_API_KEY | No | Your Llama API key for additional models |
| FLASK_ENV | No | Set to 'development' for debug mode |
| PORT | No | Custom port (default: 8080) |

## API Documentation

### /fetch (POST)
Fetches and processes an article from a URL.
- Request body: `{ "url": "article_url" }`
- Response: `{ "content": { "title", "content", "top_image_url" }, "summary" }`

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

2. **"OpenAI API Error"**
   - Verify your API key is correct
   - Check your API usage limits
   - Ensure your request isn't too long

3. **PDF Generation Fails**
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
