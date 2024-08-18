let articleTitle = '';
let topImageUrl = '';
const converter = new showdown.Converter();

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

// Function to write Hacker News links to the chatbox in a grid layout with a load button
const writeHackerNewsLinks = (links) => {
    const queryResultElement = document.getElementById('queryResult');
    queryResultElement.innerHTML = ''; // Clear any previous content

    const newsContainer = document.createElement('div');
    newsContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4';

    links.forEach(link => {
        const linkElement = document.createElement('div');
        linkElement.className = 'block p-4 bg-primary text-white rounded-lg text-center centered-container';

        // Title of the Hacker News story
        const titleElement = document.createElement('a');
        titleElement.href = link.url;
        titleElement.target = '_blank';
        titleElement.className = 'block mb-2';
        titleElement.innerText = link.title;

        // Load button for the Hacker News story
        const loadButton = document.createElement('button');
        loadButton.className = 'btn btn-secondary';
        loadButton.innerText = 'Load Article';
        loadButton.onclick = () => {
            document.getElementById('urlInput').value = link.url;
            fetchArticle(); // Fetch the article as if it were loaded from the URL input
        };

        // Append title and button to the story box
        linkElement.appendChild(titleElement);
        linkElement.appendChild(loadButton);

        // Add the story box to the container
        newsContainer.appendChild(linkElement);
    });

    queryResultElement.appendChild(newsContainer);

    // Scroll to the bottom of the chatbox
    queryResultElement.scrollTop = queryResultElement.scrollHeight;
};

// Function to fetch top 5 Hacker News stories
async function fetchHackerNews(numberOfNews=6) {
    try {
        const response = await axios.get('https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty');
        const top5Ids = response.data.slice(0, numberOfNews);

        const stories = await Promise.all(
            top5Ids.map(async (id) => {
                const storyResponse = await axios.get(`https://hacker-news.firebaseio.com/v0/item/${id}.json?print=pretty`);
                return storyResponse.data;
            })
        );

        // Display the top 5 stories in a grid layout with load buttons
        writeHackerNewsLinks(stories.map(story => ({ title: story.title, url: story.url })));

    } catch (error) {
        console.error('Error fetching Hacker News stories:', error);
        writeToChat(true, 'Error fetching Hacker News stories.', 'error');
    }
}

// Function to check if the chatbox is empty and load Hacker News if it is
function loadHackerNewsIfEmpty() {
    const queryResultElement = document.getElementById('queryResult');
    if (queryResultElement.innerHTML.trim() === "") {
        fetchHackerNews();
    }
}

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

// Load Hacker News stories if chatbox is empty on page load
window.onload = loadHackerNewsIfEmpty;
