const htmlElement = document.documentElement;

/**
 * List of available themes
 * Reduced to only light and dark themes
 */
const themes = [
    "light", "dark"
];

/**
 * Event listener to load the saved theme from localStorage and apply it.
 * This function runs when the DOM content is fully loaded.
 */
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('selectedTheme') || 'light';
    applyTheme(savedTheme);
    themeSelectElement.value = savedTheme;
});

/**
 * Function to apply the selected theme to the document and save it in localStorage.
 * @param {string} theme - The theme to be applied.
 */
const applyTheme = (theme) => {
    htmlElement.setAttribute('data-theme', theme);
    localStorage.setItem('selectedTheme', theme);
    updateThemeToggleIcon(theme);
}

/**
 * Function to toggle between light and dark themes
 */
const toggleTheme = () => {
    const currentTheme = localStorage.getItem('selectedTheme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
    themeSelectElement.value = newTheme;
}

/**
 * Update the theme toggle button icon based on the current theme
 * @param {string} theme - The current theme
 */
const updateThemeToggleIcon = (theme) => {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        if (theme === 'light') {
            themeIcon.className = 'fa-solid fa-moon'; // Moon icon for dark mode toggle
        } else {
            themeIcon.className = 'fa-solid fa-sun'; // Sun icon for light mode toggle
        }
    }
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
