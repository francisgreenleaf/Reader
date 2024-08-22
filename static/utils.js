/**
 * Function to handle the Enter key press event and trigger a specified action.
 * @param {Event} event - The keydown event.
 * @param {Function} action - The action to perform when Enter is pressed.
 */
const handleKeyDown = (event, action) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        action();
    }
}

// Function to save the API key to localStorage
document.getElementById('saveApiKeyButton').addEventListener('click', () => {
    const apiKey = document.getElementById('apiKeyInput').value;
    if (apiKey) {
        localStorage.setItem('openai_api_key', apiKey);
    }
});

// Function to retrieve the API key from localStorage
function getApiKey() {
    return localStorage.getItem('openai_api_key') || null;
}

// Function to open article modal
function openArticleModal() {
    const modal = document.getElementById('article_modal');
    const modalContent = document.getElementById('modalContent');
    const hiddenContentElement = document.getElementById('hiddenContent');
    const content = hiddenContentElement.value.trim().replace(/\n/g, '<br>');

    if (!content) {
        modalContent.innerHTML = '<p>No content available. Try loading a URL.</p>';
    } else {
        modalContent.innerHTML = content;
    }

    modal.showModal();
}

/**=====================
 * ==== FONT SELECT ====
 * =====================
 */
// Function to save font selection
function saveFontSelection() {
    const fontSelect = document.getElementById('fontSelect');
    const selectedFont = fontSelect.value;
    localStorage.setItem('chatFont', selectedFont);
    applyChatFont(selectedFont);
}

// Function to apply font to chat bubbles
function applyChatFont(font) {
    const chatStyle = document.documentElement.style;
    chatStyle.setProperty('--read-font-family', font);
}

// Load settings on page load
window.addEventListener('load', () => {
    // Existing settings load logic...

    const savedFont = localStorage.getItem('chatFont') || 'Arial';
    applyChatFont(savedFont);

    const fontSelect = document.getElementById('fontSelect');
    fontSelect.value = savedFont;
});

// Add event listener for font selection
document.getElementById('fontSelect').addEventListener('change', saveFontSelection);
