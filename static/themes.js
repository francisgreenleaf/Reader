const htmlElement = document.documentElement;

// List of available themes from DaisyUI
const themes = [
    "light", "dark", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", 
    "retro", "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", 
    "lofi", "pastel", "fantasy", "wireframe", "black", "luxury", "dracula", "cmyk", 
    "autumn", "business", "acid", "lemonade", "night", "coffee", "winter", 
    "dim", "nord", "sunset"
];

// Load the saved theme from localStorage and apply it
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
        applyTheme(savedTheme);
        themeSelectElement.value = savedTheme;
    }
});

// Function to apply the selected theme
function applyTheme(theme) {
    htmlElement.setAttribute('data-theme', theme);
    localStorage.setItem('selectedTheme', theme);
}

// Populate the theme selection dropdown
const themeSelectElement = document.getElementById('themeSelect');
themes.forEach(theme => {
    const option = document.createElement('option');
    option.value = theme;
    option.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
    themeSelectElement.appendChild(option);
});

// Listen for changes in the theme dropdown
themeSelectElement.addEventListener('change', (event) => {
    applyTheme(event.target.value);
});
