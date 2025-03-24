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
        localStorage.setItem('api_key', apiKey);
        // Show a brief confirmation message
        const saveButton = document.getElementById('saveApiKeyButton');
        const originalText = saveButton.textContent;
        saveButton.textContent = 'Saved!';
        setTimeout(() => {
            saveButton.textContent = originalText;
        }, 2000);
    }
});

// Function to retrieve the API key from localStorage
function getApiKey() {
    return localStorage.getItem('api_key') || null;
}

// Load saved API key on page load
window.addEventListener('DOMContentLoaded', () => {
    const savedApiKey = getApiKey();
    if (savedApiKey) {
        document.getElementById('apiKeyInput').value = savedApiKey;
    }
});

// Function to open article modal
function openArticleModal() {
    openArticleModalWithHighlight('');
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


function openArticleModalWithHighlight(textToHighlight) {
    const modal = document.getElementById('article_modal');
    const modalContent = document.getElementById('modalContent');
    const hiddenContentElement = document.getElementById('hiddenContent');
    let content = hiddenContentElement.value.trim();

    if (!content) {
        modalContent.innerHTML = '<p>No content available. Try loading a URL.</p>';
    } else {
        // Check if content is markdown (doesn't start with HTML tags)
        const isMarkdown = !content.trim().startsWith('<');
        
        if (isMarkdown) {
            // Convert markdown to HTML using showdown
            const converter = new showdown.Converter();
            content = converter.makeHtml(content);
        }
        
        // Escape special characters in the text to highlight for use in a regex
        if (textToHighlight) {
            const escapedText = textToHighlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(`(${escapedText})`, 'gi');
            content = content.replace(regex, '<mark>$1</mark>');
        }
        
        // If it's not markdown, replace newlines with <br> tags
        if (!isMarkdown) {
            content = content.replace(/\n/g, '<br>');
        }
        
        modalContent.innerHTML = content;
    }

    modal.showModal();

    // Scroll to the first highlighted text
    const firstHighlight = modalContent.querySelector('mark');
    if (firstHighlight) {
        firstHighlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}
