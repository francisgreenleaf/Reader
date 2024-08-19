/**
 * Function to load OSF preprints into the specified container.
 * @param {HTMLElement} container - The container to load the content into.
 * @param {HTMLElement} loadMoreButton - The "Load More" button.
 */
const loadOSFPreprints = async (container, loadMoreButton) => {
    try {
        const response = await axios.get('https://api.osf.io/v2/preprints/?format=json&page=1&page_size=6');
        const preprints = response.data.data;

        const preprintElements = preprints.map(preprint => {
            const attributes = preprint.attributes;
            return `
                <div class="relative flex flex-col justify-center p-4 bg-primary text-white rounded-lg pb-10 text-center">
                    <!-- Title of the OSF preprint -->
                    <a href="${attributes.links.html}" target="_blank" class="font-bold text-lg mb-2">
                        ${attributes.title}
                    </a>
                    <!-- Load Button -->
                    <button class="btn w-32 m-auto" onclick="document.getElementById('urlInput').value='${attributes.links.html}'; fetchArticle();', '_blank');">
                        Load <i class="fa-solid fa-download ml-2"></i>
                    </button>
                    <!-- Author (positioned at the bottom) -->
                    <span class="absolute bottom-2 left-2 bg-gray-700 text-white rounded-full px-3 py-1 text-xs">
                        Author: ${attributes.contributors[0].name}
                    </span>
                </div>
            `;
        });

        // Append the preprints to the container
        container.innerHTML = preprintElements.join('');

        // Hide the "Load More" button after loading
        loadMoreButton.style.display = 'none';

    } catch (error) {
        writeToChat(true, `Error fetching OSF preprints.`, 'error');
        console.error('Error fetching OSF preprints:', error);
    }
};
