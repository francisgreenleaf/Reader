/**
 * Function to write a new section (title + content) to the chatbox without clearing previous content.
 * @param {string} title - The title of the section.
 * @param {Array} elements - Array of HTML strings representing individual elements (links, papers, etc.).
 */
const writeSectionToChat = (title, elements) => {
    const queryResultElement = document.getElementById('queryResult');

    // Add the title element
    const titleElement = `
        <div class="w-full text-center my-4">
            <h2 class="text-2xl font-bold">${title}</h2>
            <hr class="border-t-2 border-gray-300 mb-6">
        </div>
    `;
    queryResultElement.innerHTML += titleElement;

    // Create a container for the elements
    const container = document.createElement('div');
    container.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 m-6';

    // Add each element to the container
    elements.forEach(elementHTML => {
        container.innerHTML += elementHTML;
    });

    // Append the container to the chatbox
    queryResultElement.appendChild(container);

    // Scroll to the bottom of the chatbox
    queryResultElement.scrollTop = queryResultElement.scrollHeight;
};

/**
 * Function to write Hacker News links to the chatbox.
 * @param {Array} links - Array of objects containing Hacker News links, titles, scores, and authors.
 */
const writeHackerNewsLinks = (links) => {
    const elements = links.map(link => {
        return `
            <div class="relative flex flex-col justify-center p-4 bg-primary text-white rounded-lg pb-10 text-center">
                <!-- Title of the Hacker News story -->
                <a href="${link.url}" target="_blank" class="font-bold text-lg mb-2">
                    ${link.title}
                </a>
                <!-- Load Button -->
                <button class="btn w-32 m-auto" onclick="document.getElementById('urlInput').value='${link.url}'; fetchArticle();">
                    Load <i class="fa-solid fa-download ml-2"></i>
                </button>
                <!-- Score (positioned at the bottom right) -->
                <span class="absolute bottom-2 right-2 bg-yellow-500 text-black rounded-full px-3 py-1 text-xs">
                    Score: ${link.score}
                </span>
                <!-- Author (positioned at the bottom left) -->
                <a href="https://news.ycombinator.com/user?id=${link.by}" target="_blank" class="absolute bottom-2 left-2 bg-gray-700 text-white rounded-full px-3 py-1 text-xs">
                    By: ${link.by}
                </a>
            </div>
        `;
    });

    writeSectionToChat("Hacker News", elements);
};

/**
 * Function to write Arxiv papers to the chatbox.
 * @param {Array} papers - Array of objects containing Arxiv papers, titles, authors, and links.
 */
const writeArxivPapers = (papers) => {
    const elements = papers.map(paper => {
        return `
            <div class="relative flex flex-col justify-center p-4 bg-primary text-white rounded-lg pb-10 text-center">
                <!-- Title of the Arxiv paper -->
                <a href="${paper.link}" target="_blank" class="font-bold text-lg mb-2">
                    ${paper.title}
                </a>
                <!-- Authors -->
                <span class=" rounded-4 px-3 py-1 text-xs">
                    Authors: ${paper.authors}
                </span>
                <!-- Load Button -->
                <button class="btn w-32 m-auto" onclick="window.open('${paper.link}', '_blank');">
                    Load <i class="fa-solid fa-download ml-2"></i>
                </button>
            </div>
        `;
    });

    writeSectionToChat("Arxiv Papers", elements);
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
};

/**
 * Function to fetch the latest Arxiv papers and display them in the chatbox.
 * @param {number} [numberOfPapers=6] - Number of Arxiv papers to fetch.
 */
const fetchArxivPapers = async (numberOfPapers = 6) => {
    try {
        const response = await axios.get(`http://export.arxiv.org/api/query?search_query=all&start=0&max_results=${numberOfPapers}&sortBy=lastUpdatedDate&sortOrder=descending`);
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(response.data, "text/xml");

        const entries = xmlDoc.getElementsByTagName("entry");
        const papers = Array.from(entries).map(entry => {
            const title = entry.getElementsByTagName("title")[0].textContent.trim();
            const authors = Array.from(entry.getElementsByTagName("author")).map(author => author.getElementsByTagName("name")[0].textContent.trim()).join(", ");
            const link = entry.getElementsByTagName("id")[0].textContent.trim();
            return { title, authors, link };
        });

        writeArxivPapers(papers);

    } catch (error) {
        writeToChat(true, `Error fetching Arxiv papers.`, 'error');
        console.error('Error fetching Arxiv papers:', error);
    }
};

/**
 * Function to load both Arxiv papers and Hacker News stories when the chatbox is empty.
 */
const loadContentIfEmpty = () => {
    const queryResultElement = document.getElementById('queryResult');
    if (queryResultElement.innerHTML.trim() === "") {
        fetchArxivPapers();
        fetchHackerNews();
    }
};

window.onload = loadContentIfEmpty;
