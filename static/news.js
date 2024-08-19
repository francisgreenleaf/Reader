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


// Initialize sections with "Load More" buttons
// Initialize sections with "Load More" buttons
window.onload = () => {
    writeSectionToChat('Hacker News', loadHackerNewsLinks);
    writeSectionToChat('Arxiv Papers', loadArxivPapers);
    writeSectionToChat('GDELT News', loadGDELTNews);
    writeSectionToChat('OSF Preprints', loadOSFPreprints);
};
