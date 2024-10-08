const htmlElement = document.documentElement;

/**
 * List of available themes from DaisyUI
 * https://daisyui.com/docs/themes/
 */
const themes = [
    "light", "dark", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", 
    "retro", "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", 
    "lofi", "pastel", "fantasy", "wireframe", "black", "luxury", "dracula", "cmyk", 
    "autumn", "business", "acid", "lemonade", "night", "coffee", "winter", 
    "dim", "nord", "sunset"
];

/**
 * Event listener to load the saved theme from localStorage and apply it.
 * This function runs when the DOM content is fully loaded.
 */
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
        applyTheme(savedTheme);
        themeSelectElement.value = savedTheme;
    }
});

/**
 * Function to apply the selected theme to the document and save it in localStorage.
 * @param {string} theme - The theme to be applied.
 */
const applyTheme = (theme) => {
    htmlElement.setAttribute('data-theme', theme);
    localStorage.setItem('selectedTheme', theme);
}

/**
 * Populate the theme selection dropdown with the available themes.
 */
const themeSelectElement = document.getElementById('themeSelect');
themes.forEach(theme => {
    const option = document.createElement('option');
    option.value = theme;
    option.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
    themeSelectElement.appendChild(option);
});

/**
 * Event listener for changes in the theme dropdown selection.
 * When the user selects a new theme, the theme is applied.
 */
themeSelectElement.addEventListener('change', (event) => {
    applyTheme(event.target.value);
});
