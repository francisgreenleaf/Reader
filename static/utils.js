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
