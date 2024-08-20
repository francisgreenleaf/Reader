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
        <div class="w-full text-center my-4">
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
    contentContainer.className = 'content-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 m-6';

    sectionWrapper.appendChild(loadMoreButton); // Append Load More button to the section wrapper
    sectionWrapper.appendChild(contentContainer); // Append content container
    queryResultElement.appendChild(sectionWrapper); // Append the section wrapper to the query result element

    // Scroll to the bottom of the chatbox
    queryResultElement.scrollTop = queryResultElement.scrollHeight;
};

// Initialize sections with "Load More" buttons
window.onload = () => {
    writeSectionToChat('Hacker News', loadHackerNewsLinks);
    writeSectionToChat('Arxiv Papers', loadArxivPapers);
    writeSectionToChat('GDELT News', loadGDELTNews);
    writeSectionToChat('OSF Preprints', loadOSFPreprints);
};
