/**
 * Function to load GDELT news articles into the specified container.
 * @param {HTMLElement} container - The container to load the content into.
 * @param {HTMLElement} loadMoreButton - The "Load More" button.
 */
const loadGDELTNews = async (container, loadMoreButton) => {
    try {
        const response = await axios.get('https://api.gdeltproject.org/api/v2/doc/doc?query=technology&mode=artlist&maxrecords=6&format=json');
        const articles = response.data.articles;

        const articleElements = articles.map(article => {
            return `
                <div class="relative flex flex-col justify-center p-4 bg-primary text-white rounded-lg pb-10 text-center">
                    <!-- Title of the GDELT article -->
                    <a href="${article.url}" target="_blank" class="font-bold text-lg mb-2">
                        ${article.title}
                    </a>
                    <!-- Load Button -->
                    <button class="btn w-32 m-auto" onclick="document.getElementById('urlInput').value='${article.url}'; fetchArticle();">
                        Load <i class="fa-solid fa-download ml-2"></i>
                    </button>
                    <!-- Source (positioned at the bottom) -->
                    <span class="absolute bottom-2 left-2 bg-gray-700 text-white rounded-full px-3 py-1 text-xs">
                        Source: ${article.source}
                    </span>
                </div>
            `;
        });

        // Append the articles to the container
        container.innerHTML = articleElements.join('');

        // Hide the "Load More" button after loading
        loadMoreButton.style.display = 'none';

    } catch (error) {
        writeToChat(true, `Error fetching GDELT news.`, 'error');
        console.error('Error fetching GDELT news:', error);
    }
};
