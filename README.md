# Reader App

The Reader App is a web application that allows users to fetch articles from a given URL, view the content, generate a PDF version of the article, and query the article using natural language processing techniques. This repository contains two versions of the Reader App: a Streamlit version and a Flask version.

## Streamlit Version

### Dependencies

To run the Streamlit version of the Reader App, you need to have the following dependencies installed:

- streamlit
- newspaper3k
- html
- base64
- io
- reportlab
- openai
- llama_index
- langchain_community
- os

You can install these dependencies using the following command:

%pip install streamlit newspaper3k reportlab openai llama_index langchain_community

### Setup

1. Clone this repository to your local machine.

2. Navigate to the project directory.

3. Set your OpenAI API key as an environment variable named `OPENAI_API_KEY`. You can do this by creating a .env file and assigning your API key there. 

4. Run the Streamlit app using the following command:

streamlit run streamlitversion.py

5. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

## Flask Version

### Dependencies

To run the Flask version of the Reader App, you need to have the following dependencies installed:

- flask
- flask_caching
- newspaper3k
- html
- reportlab
- io
- os
- openai
- requests
- base64
- PIL
- llama_index
- langchain_community
- logging

You can install these dependencies using the following command:

%pip install flask flask_caching newspaper3k reportlab openai requests Pillow llama_index langchain_community

### Setup

1. Clone this repository to your local machine.

2. Navigate to the project directory.

3. Set your OpenAI API key as an environment variable named `OPENAI_API_KEY`. You can do this by creating a .env file and assigning your API key there.


4. Run the Flask app using the following command:

python app.py

5. Open your web browser and go to `http://localhost:8080` to access the Reader App.

## Usage

1. Enter the URL of the article you want to fetch in the provided input field.

2. Click the "Fetch Article" button to retrieve the article content.

3. The article's title, summary, and content will be displayed on the page.

4. You can download a PDF version of the article by clicking the "Download as PDF" button.

5. To query the article, enter your query in the provided input field and click the "Submit Query" button.

6. The app will process your query using natural language processing techniques and display the relevant information from the article.

## Contributing

If you'd like to contribute to the Reader App, feel free to submit a pull request or open an issue on the GitHub repository.

## License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
