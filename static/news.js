// Function to write Hacker News links to the chatbox in a grid layout with a load button
const writeHackerNewsLinks = (links) => {
    const queryResultElement = document.getElementById('queryResult');
    queryResultElement.innerHTML = ''; // Clear any previous content

    const newsContainer = document.createElement('div');
    newsContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 m-6';

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

// Load Hacker News stories if chatbox is empty on page load
window.onload = loadHackerNewsIfEmpty;
