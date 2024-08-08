# Reader App

The Reader App is a web application that allows users to fetch articles from a given URL, view the content, generate a PDF version of the article, and query the article using natural language processing techniques. This repository contains two versions of the Reader App: a **Streamlit** version and a **Flask** version.
## Setup

1. Clone this repository to your local machine.

2. Navigate to the project directory `cd Reader`.

3. Create a .env file in the project directory and set your OpenAI API key as an environment variable:
    `OPENAI_API_KEY=YOUR_REAL_KEY`

4. Next, choose wich version you want **Stremlit** or **Flask**.

### 1. Streamlit Version

1. Install the required dependencies:
   ```sh
    pip install -r requirements_streamlit.txt
    ```

2. Run the Streamlit app using the following command:
    ```sh
    streamlit run streamlitversion.py
    ```

3. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

### 2. Flask Version

1. Install the required dependencies:
   ```sh
    pip install -r requirements_flask.txt
    ```

2. Run the Streamlit app using the following command:
    ```sh
    python app.py
    ```

3. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8080`).

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

This project is open-source and available under the [Apache License 2.0](https://opensource.org/licenses/MIT).
