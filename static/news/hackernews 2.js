/** 
 * Function to load Hacker News links into the specified container.
 * @param {HTMLElement} container - The container to load the content into.
 * @param {HTMLElement} loadMoreButton - The "Load More" button.
 */
const loadHackerNewsLinks = async (container, loadMoreButton) => {
    return loadNewsContent(async (container, loadMoreButton) => {
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
    }, container, loadMoreButton);
};
