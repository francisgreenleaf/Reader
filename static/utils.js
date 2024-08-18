// Function to handle Enter key press
function handleKeyDown(event, action) {
    if (event.key === 'Enter') {
        event.preventDefault();
        action();
    }
}
