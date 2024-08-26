// Global variables
let articleTitle = '';
let topImageUrl = '';
let defaultModel = 'gpt-4o-mini';
let apiKey = '';

// List of available themes
const themes = [
    'light', 'dark', 'cupcake', 'bumblebee', 'emerald', 'corporate', 'synthwave', 
    'retro', 'halloween', 'garden', 'forest', 'aqua', 
    'lofi', 'fantasy', 'wireframe', 'black', 'luxury', 'dracula', 'business', 'night', 'coffee', 'winter',
];

// Function to fetch article
async function fetchArticle() {
    const url = document.getElementById('urlInput').value;
    const errorElement = document.getElementById('error');
    const contentElement = document.getElementById('content');
    const hiddenContentElement = document.getElementById('hiddenContent');
    const summaryElement = document.getElementById('summary');
    const articleTitleElement = document.getElementById('articleTitle');
    const summaryLoadingElement = document.getElementById('summaryLoading');
    const contentLoadingElement = document.getElementById('contentLoading');

    errorElement.textContent = '';
    contentElement.innerHTML = '';
    summaryElement.innerHTML = '';
    hiddenContentElement.value = '';
    summaryLoadingElement.classList.remove('hidden');
    contentLoadingElement.classList.remove('hidden');

    try {
        const response = await axios.post('/fetch', { url: url });
        const article = response.data.content;
        const summary = response.data.summary;
        articleTitle = article.title;
        topImageUrl = article.top_image_url;

        articleTitleElement.childNodes[0].textContent = article.title;

        const articleContent = article.content.replace(/\n/g, '<br>');
        contentElement.innerHTML = topImageUrl !== '' ? `
            <h3 class="text-xl font-semibold mb-4">Content:</h3>
            <img id="top-image" src=${topImageUrl}>
            <p>${articleContent}</p>
        `: `
            <h3 class="text-xl font-semibold mb-4">Content:</h3>
            <p>${articleContent}</p>
        `;

        hiddenContentElement.value = article.content;

        summaryElement.innerHTML = `
            <p>${summary}</p>
        `;

    } catch (error) {
        errorElement.textContent = 'Error fetching article: ' + (error.response?.data?.error || error.message);
    } finally {
        summaryLoadingElement.classList.add('hidden');
        contentLoadingElement.classList.add('hidden');
    }
}

// Function to generate PDF
async function generatePDF() {
    const hiddenContentElement = document.getElementById('hiddenContent');
    const content = hiddenContentElement.value.trim();
    const top_image_url = document.getElementById('top-image') ?
        document.getElementById('top-image').src : '';

    if (!content) {
        console.error('Content is empty. Cannot generate PDF.');
        return;
    }

    try {
        const response = await axios.post('/generate_pdf', { title: articleTitle, content: content, imageUrl: top_image_url }, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${articleTitle.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`);
        document.body.appendChild(link);
        link.click();
    } catch (error) {
        console.error('Error generating PDF:', error);
    }
}

// Function to query article
async function queryArticle() {
    const query = document.getElementById('queryInput').value;
    const model = document.getElementById('modelSelect').value;
    const hiddenContentElement = document.getElementById('hiddenContent');
    const queryResultElement = document.getElementById('queryResult');
    const queryLoadingElement = document.getElementById('queryLoading');
    const content = hiddenContentElement.value.trim();

    queryResultElement.textContent = '';
    queryLoadingElement.classList.remove('hidden');

    if (!content) {
        console.error('Content is empty. Cannot perform query.');
        queryResultElement.textContent = 'Error: Content is empty. Please load an article';
        queryLoadingElement.classList.add('hidden');
        return;
    }

    try {
        const response = await axios.post('/query', { content: content, query: query, model: model, apiKey: apiKey });
        queryResultElement.textContent = response.data.result;
    } catch (error) {
        queryResultElement.textContent = 'Error querying article: ' + (error.response?.data?.error || error.message);
    } finally {
        queryLoadingElement.classList.add('hidden');
    }
}

// Function to open settings modal
function openSettingsModal() {
    const modal = document.getElementById('settings_modal');
    modal.showModal();
    loadSettings();
}

// Function to close settings modal
function closeSettingsModal() {
    const modal = document.getElementById('settings_modal');
    modal.close();
}

// Function to load current settings
function loadSettings() {
    const apiKeyInput = document.getElementById('apiKeyInput');
    const modelSelect = document.getElementById('modelSelect');
    const themeSelect = document.getElementById('themeSelect');

    apiKeyInput.value = apiKey;
    modelSelect.value = defaultModel;

    themeSelect.innerHTML = themes.map(theme => 
        `<option value="${theme}"${theme === getCurrentTheme() ? ' selected' : ''}>${theme}</option>`
    ).join('');
}

// Function to save API key
function saveApiKey() {
    const apiKeyInput = document.getElementById('apiKeyInput');
    apiKey = apiKeyInput.value;
    localStorage.setItem('apiKey', apiKey);
    console.log('API key saved!');
}

// Function to save model selection
function saveModelSelection() {
    const modelSelect = document.getElementById('modelSelect');
    defaultModel = modelSelect.value;
    localStorage.setItem('defaultModel', defaultModel);
    document.getElementById('modelSelect').value = defaultModel;
}

// Function to save theme selection
function saveThemeSelection() {
    const themeSelect = document.getElementById('themeSelect');
    const selectedTheme = themeSelect.value;
    localStorage.setItem('theme', selectedTheme);
    applyTheme(selectedTheme);
}

// Function to get current theme
function getCurrentTheme() {
    return localStorage.getItem('theme') || 'light';
}

// Function to apply theme
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

// Load settings on page load
window.addEventListener('load', () => {
    defaultModel = localStorage.getItem('defaultModel') || 'gpt-4o-mini';
    apiKey = localStorage.getItem('apiKey') || '';
    
    document.getElementById('modelSelect').value = defaultModel;

    const savedTheme = getCurrentTheme();
    applyTheme(savedTheme);

    const themeSelect = document.getElementById('themeSelect');
    themeSelect.innerHTML = themes.map(theme => 
        `<option value="${theme}"${theme === savedTheme ? ' selected' : ''}>${theme}</option>`
    ).join('');
});

// Add event listeners
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('settingsBtn').addEventListener('click', openSettingsModal);
    document.getElementById('saveApiKeyButton').addEventListener('click', saveApiKey);
    document.getElementById('modelSelect').addEventListener('change', saveModelSelection);
    document.getElementById('themeSelect').addEventListener('change', saveThemeSelection);
    document.getElementById('loadButton').addEventListener('click', fetchArticle);
    document.getElementById('generatePdfButton').addEventListener('click', generatePDF);
    document.getElementById('submitQueryButton').addEventListener('click', queryArticle);
});