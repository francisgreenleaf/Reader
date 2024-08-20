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
    sectionWrapper.className = 'card bg-base-100 shadow-lg m-4 py-2 relative';

    // Add the title element
    const titleElement = `
        <div class="w-full text-center">
            <h2 class="text-2xl font-bold">${title}</h2>
            <hr class="border-t-2 border-gray-300 mb-6">
        </div>
    `;
    sectionWrapper.innerHTML = titleElement;

    // Create a "Load More" button and position it in the top right corner
    const loadMoreButton = document.createElement('button');
    loadMoreButton.className = 'btn absolute top-2 right-2';
    loadMoreButton.textContent = 'Load';
    loadMoreButton.onclick = () => {
        loadFunction(contentContainer, loadMoreButton);
    };

    // Create a container for the content
    const contentContainer = document.createElement('div');
    contentContainer.className = 'content-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mx-6 mb-4 mt-0';

    sectionWrapper.appendChild(loadMoreButton);
    sectionWrapper.appendChild(contentContainer);
    queryResultElement.appendChild(sectionWrapper);

    // Scroll to the bottom of the chatbox
    queryResultElement.scrollTop = queryResultElement.scrollHeight;
};

const loadNewsContent = async (loadFunction, container, loadMoreButton) => {
    const queryLoadingElement = document.createElement('div');
    queryLoadingElement.className = 'absolute inset-0 flex justify-center items-center bg-opacity-75 bg-white z-50'; // Add absolute positioning and styling for centering
    queryLoadingElement.innerHTML = `
        <svg class="animate-spin h-8 w-8 mr-3" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        Loading...
    `;
    container.style.position = 'relative'; // Ensure the container has relative positioning
    container.appendChild(queryLoadingElement); // Show loading spinner

    try {
        await loadFunction(container, loadMoreButton);
    } finally {
        container.removeChild(queryLoadingElement); // Hide loading spinner
    }
}


// Initialize sections with "Load More" buttons
window.onload = () => {
    writeSectionToChat('Hacker News', loadHackerNewsLinks);
    writeSectionToChat('Arxiv Papers', loadArxivPapers);
    writeSectionToChat('GDELT News', loadGDELTNews);
    writeSectionToChat('OSF Preprints', loadOSFPreprints);
};
