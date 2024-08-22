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

// Function to save font selection
function saveFontSelection() {
    const fontSelect = document.getElementById('fontSelect');
    const selectedFont = fontSelect.value;
    localStorage.setItem('chatFont', selectedFont);
    applyChatFont(selectedFont);
}

// Function to apply font to chat bubbles
function applyChatFont(font) {
    const chatBubbles = document.querySelectorAll('.chat-bubble');
    chatBubbles.forEach(bubble => {
        bubble.style.fontFamily = font;
    });
}

// Load settings on page load
window.addEventListener('load', () => {
    // Existing settings load logic...

    const savedFont = localStorage.getItem('chatFont') || 'sans-serif';
    applyChatFont(savedFont);

    const fontSelect = document.getElementById('fontSelect');
    fontSelect.value = savedFont;
});

// Add event listener for font selection
document.getElementById('fontSelect').addEventListener('change', saveFontSelection);
