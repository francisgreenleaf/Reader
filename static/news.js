/**
 * Function to write Hacker News links to the chatbox in a grid layout with a load button.
 * @param {Array} links - Array of objects containing Hacker News links, titles, scores, and authors.
 */
const writeHackerNewsLinks = (links) => {
    const queryResultElement = document.getElementById('queryResult');
    queryResultElement.innerHTML = ''; // Clear any previous content

    const newsContainer = document.createElement('div');
    newsContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 m-6';

    links.forEach(link => {
        const linkHTML = `
            <div class="relative flex flex-col justify-center p-4 bg-primary text-white rounded-lg pb-10 text-center">
                <a href="${link.url}" target="_blank" class="font-bold text-lg mb-2">
                    ${link.title}
                </a>

                <button class="btn w-32 m-auto" onclick="document.getElementById('urlInput').value='${link.url}'; fetchArticle();">
                    Load <i class="fa-solid fa-download ml-2"></i>
                </button>

                <span class="absolute bottom-2 right-2 bg-yellow-500 text-black rounded-full px-3 py-1 text-xs">
                    Score: ${link.score}
                </span>

                <a href="https://news.ycombinator.com/user?id=${link.by}" target="_blank" class="absolute bottom-2 left-2 bg-gray-700 text-white rounded-full px-3 py-1 text-xs">
                    By: ${link.by}
                </a>
            </div>
        `;

        // Append the HTML to the container
        newsContainer.innerHTML += linkHTML;
    });

    queryResultElement.appendChild(newsContainer);

    // Scroll to the bottom of the chatbox
    queryResultElement.scrollTop = queryResultElement.scrollHeight;
};


/**
 * Function to fetch the top Hacker News stories and display them in the chatbox.
 * @param {number} [numberOfNews=6] - Number of top Hacker News stories to fetch.
 */
const fetchHackerNews = async (numberOfNews = 6) => {
    try {
        const response = await axios.get('https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty');
        const topIds = response.data.slice(0, numberOfNews);

        const stories = await Promise.all(
            topIds.map(async (id) => {
                const storyResponse = await axios.get(`https://hacker-news.firebaseio.com/v0/item/${id}.json?print=pretty`);
                const story = storyResponse.data;
                console.log(story);
                
                // If story.url is missing, construct the URL using the Hacker News item ID
                const url = story.url ? story.url : `https://news.ycombinator.com/item?id=${story.id}`;

                return { title: story.title, url: url, by: story.by, score: story.score };
            })
        );

        writeHackerNewsLinks(stories);

    } catch (error) {
        writeToChat(true, `Error fetching Hacker News stories.`, 'error');
        console.error('Error fetching Hacker News stories:', error);
    }
}


/**
 * Function to check if the chatbox is empty and load Hacker News stories if it is.
 */
const loadNewsIfEmpty = () => {
    const queryResultElement = document.getElementById('queryResult');
    if (queryResultElement.innerHTML.trim() === "") {
        fetchHackerNews();
    }
}

// Load Hacker News stories if chatbox is empty on page load
window.onload = loadNewsIfEmpty;
