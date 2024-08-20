/**
 * Function to load Arxiv papers into the specified container.
 * @param {HTMLElement} container - The container to load the content into.
 * @param {HTMLElement} loadMoreButton - The "Load More" button.
 */
const loadArxivPapers = async (container, loadMoreButton) => {
    return loadNewsContent(async (container, loadMoreButton) => {
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
                        <button class="btn w-32 m-auto" onclick="document.getElementById('urlInput').value='${link}'; fetchArticle();">
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
    }, container, loadMoreButton);
}
