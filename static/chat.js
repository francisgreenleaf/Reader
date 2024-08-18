const converter = new showdown.Converter();
let articleTitle = '';
let topImageUrl = '';

// Function to write messages to the chatbox
const writeToChat = (isAI, message, color="") => {
    const queryResultElement = document.getElementById('queryResult');
    
    // Create the chat bubble element
    const chatBubble = document.createElement('div');
    chatBubble.className = `chat-bubble ${color === "" ? "" : "chat-bubble-" + color}`;
    chatBubble.innerHTML = converter.makeHtml(message);

    // Create the chat container element
    const chatContainer = document.createElement('div');
    chatContainer.className = `chat chat-${isAI ? 'start' : 'end'}`;
    chatContainer.appendChild(chatBubble);

    // Append the chat container to the chatbox
    queryResultElement.appendChild(chatContainer);

    // Scroll to the bottom of the chatbox
    queryResultElement.scrollTop = queryResultElement.scrollHeight;
};

// Function to fetch an article and display it in the chatbox
async function fetchArticle() {
    const url = document.getElementById('urlInput').value;
    const errorElement = document.getElementById('error');
    const hiddenContentElement = document.getElementById('hiddenContent'); // Hidden element for storing content

    errorElement.textContent = '';
    hiddenContentElement.value = ''; // Clear the hidden content field

    try {
        const response = await axios.post('/fetch', { url: url });
        const article = response.data.content;
        articleTitle = article.title;
        topImageUrl = article.top_image_url;

        writeToChat(true, `##${articleTitle}\n\n${article.summary}`, 'primary');

        hiddenContentElement.value = article.content; // Store raw content in hidden element

    } catch (error) {
        errorElement.textContent = 'Error fetching article: ' + (error.response?.data?.error || error.message);
    }
}

// Function to generate a PDF of the article
async function generatePDF() {
    const hiddenContentElement = document.getElementById('hiddenContent');
    const content = hiddenContentElement.value.trim();
    const images = [];

    if (!content) {
        console.error('Content is empty. Cannot generate PDF.');
        return;
    }

    try {
        const response = await axios.post('/generate_pdf', { title: articleTitle, content: content, images: images }, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${articleTitle.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`);
        document.body.appendChild(link);
        link.click();
    } catch (error) {
        console.error('Error generating PDF:', error);
    }
}

// Function to send a query to the article and display the result in the chatbox
async function queryArticle() {
    const query = document.getElementById('queryInput').value;
    writeToChat(false, query);
    const model = document.getElementById('modelSelect').value;
    const hiddenContentElement = document.getElementById('hiddenContent');
    const queryLoadingElement = document.getElementById('queryLoading');
    const content = hiddenContentElement.value.trim();

    queryLoadingElement.classList.remove('hidden');

    if (!content) {
        console.error('Content is empty. Cannot perform query.');
        writeToChat(true, `Error: Content is empty. Please load an article`, 'error');
        queryLoadingElement.classList.add('hidden');
        return;
    }

    try {
        const response = await axios.post('/query', { content: content, query: query, model: model });
        writeToChat(true, response.data.result);
    } catch (error) {
        writeToChat(true, `Error querying article: ${error.response?.data?.error || error.message}`, 'error');
    } finally {
        queryLoadingElement.classList.add('hidden');
    }
}
