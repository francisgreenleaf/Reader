/**
 * Function to write a new section (title + content) to the chatbox without clearing previous content.
 * The section will only load content when the "Load More" button is clicked.
 * @param {string} title - The title of the section.
 * @param {Function} loadFunction - Function to be called when the "Load More" button is clicked.
 */
const writeSectionToChat = (title, loadFunction) => {
    const queryResultElement = document.getElementById('queryResult');

    // Create a wrapper for the section
    const sectionWrapper = document.createElement('div');
    sectionWrapper.className = 'section-wrapper my-4';

    // Add the title element
    const titleElement = `
        <div class="w-full text-center my-4">
            <h2 class="text-2xl font-bold">${title}</h2>
            <hr class="border-t-2 border-gray-300 mb-6">
        </div>
    `;
    sectionWrapper.innerHTML = titleElement;

    // Create a container for the content
    const contentContainer = document.createElement('div');
    contentContainer.className = 'content-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 m-6';

    // Create a "Load More" button
    const loadMoreButton = document.createElement('button');
    loadMoreButton.className = 'btn w-full mt-4';
    loadMoreButton.textContent = 'Load More';
    loadMoreButton.onclick = () => {
        loadFunction(contentContainer, loadMoreButton);
    };

    sectionWrapper.appendChild(loadMoreButton);
    sectionWrapper.appendChild(contentContainer);
    queryResultElement.appendChild(sectionWrapper);

    // Scroll to the bottom of the chatbox
    queryResultElement.scrollTop = queryResultElement.scrollHeight;
};

/**
 * Function to load Hacker News links into the specified container.
 * @param {HTMLElement} container - The container to load the content into.
 * @param {HTMLElement} loadMoreButton - The "Load More" button.
 */
const loadHackerNewsLinks = async (container, loadMoreButton) => {
    try {
        const response = await axios.get('https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty');
        const topIds = response.data.slice(0, 6); // Load the first 6 stories

        const stories = await Promise.all(
            topIds.map(async (id) => {
                const storyResponse = await axios.get(`https://hacker-news.firebaseio.com/v0/item/${id}.json?print=pretty`);
                const story = storyResponse.data;

                // If story.url is missing, construct the URL using the Hacker News item ID
                const url = story.url ? story.url : `https://news.ycombinator.com/item?id=${story.id}`;

                return `
                    <div class="relative flex flex-col justify-center p-4 bg-primary text-white rounded-lg pb-10 text-center">
                        <!-- Title of the Hacker News story -->
                        <a href="${url}" target="_blank" class="font-bold text-lg mb-2">
                            ${story.title}
                        </a>
                        <!-- Load Button -->
                        <button class="btn w-32 m-auto" onclick="document.getElementById('urlInput').value='${url}'; fetchArticle();">
                            Load <i class="fa-solid fa-download ml-2"></i>
                        </button>
                        <!-- Score (positioned at the bottom right) -->
                        <span class="absolute bottom-2 right-2 bg-yellow-500 text-black rounded-full px-3 py-1 text-xs">
                            Score: ${story.score}
                        </span>
                        <!-- Author (positioned at the bottom left) -->
                        <a href="https://news.ycombinator.com/user?id=${story.by}" target="_blank" class="absolute bottom-2 left-2 bg-gray-700 text-white rounded-full px-3 py-1 text-xs">
                            By: ${story.by}
                        </a>
                    </div>
                `;
            })
        );

        // Append the stories to the container
        container.innerHTML = stories.join('');

        // Hide the "Load More" button after loading
        loadMoreButton.style.display = 'none';

    } catch (error) {
        writeToChat(true, `Error fetching Hacker News stories.`, 'error');
        console.error('Error fetching Hacker News stories:', error);
    }
};

/**
 * Function to load Arxiv papers into the specified container.
 * @param {HTMLElement} container - The container to load the content into.
 * @param {HTMLElement} loadMoreButton - The "Load More" button.
 */
const loadArxivPapers = async (container, loadMoreButton) => {
    try {
        const response = await axios.get(`http://export.arxiv.org/api/query?search_query=all&start=0&max_results=6&sortBy=lastUpdatedDate&sortOrder=descending`);
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(response.data, "text/xml");

        const entries = xmlDoc.getElementsByTagName("entry");
        const papers = Array.from(entries).map(entry => {
            const title = entry.getElementsByTagName("title")[0].textContent.trim();
            const authors = Array.from(entry.getElementsByTagName("author")).map(author => author.getElementsByTagName("name")[0].textContent.trim()).join(", ");
            const link = entry.getElementsByTagName("id")[0].textContent.trim();
            return `
                <div class="relative flex flex-col justify-center p-4 bg-primary text-white rounded-lg pb-10 text-center">
                    <!-- Title of the Arxiv paper -->
                    <a href="${link}" target="_blank" class="font-bold text-lg mb-2">
                        ${title}
                    </a>
                    <!-- Authors -->
                    <span class="block mb-2 text-sm">
                        Authors: ${authors}
                    </span>
                    <!-- Load Button -->
                    <button class="btn w-32 m-auto" onclick="window.open('${link}', '_blank');">
                        Load <i class="fa-solid fa-download ml-2"></i>
                    </button>
                </div>
            `;
        });

        // Append the papers to the container
        container.innerHTML = papers.join('');

        // Hide the "Load More" button after loading
        loadMoreButton.style.display = 'none';

    } catch (error) {
        writeToChat(true, `Error fetching Arxiv papers.`, 'error');
        console.error('Error fetching Arxiv papers:', error);
    }
};

// Initialize sections with "Load More" buttons
window.onload = () => {
    writeSectionToChat('Hacker News', loadHackerNewsLinks);
    writeSectionToChat('Arxiv Papers', loadArxivPapers);
};
