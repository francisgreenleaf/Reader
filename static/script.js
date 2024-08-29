let articleTitle = '';
let topImageUrl = ''

async function fetchArticle() {
    const url = document.getElementById('urlInput').value;
    const errorElement = document.getElementById('error');
    const contentElement = document.getElementById('content');
    const hiddenContentElement = document.getElementById('hiddenContent'); // Hidden element for storing content
    const summaryElement = document.getElementById('summary');
    const articleTitleElement = document.getElementById('articleTitle');
    const summaryLoadingElement = document.getElementById('summaryLoading');
    const contentLoadingElement = document.getElementById('contentLoading');
    const summaryCollapse = document.getElementById('summaryCollapse');

    errorElement.textContent = '';
    contentElement.innerHTML = '';
    summaryElement.innerHTML = '';
    hiddenContentElement.value = ''; // Clear the hidden content field
    summaryLoadingElement.classList.remove('hidden');
    contentLoadingElement.classList.remove('hidden');

    try {
        const response = await axios.post('/fetch', { url: url });
        const article = response.data.content;
        articleTitle = article.title;
        topImageUrl = article.top_image_url;

        articleTitleElement.childNodes[0].textContent = article.title;

        const articleContent = article.content.replace(/\n/g, '<br>');
        contentElement.innerHTML = `
            <h3 class="text-xl font-semibold mb-4">Content:</h3>
            <img src=${topImageUrl}>
            <p>${articleContent}</p>
        `;

        hiddenContentElement.value = article.content; // Store raw content in hidden element

        summaryElement.innerHTML = `
            <p>${article.summary}</p>
        `;

        // Automatically open the summary collapse
        summaryCollapse.checked = true;

    } catch (error) {
        errorElement.textContent = 'Error fetching article: ' + (error.response?.data?.error || error.message);
    } finally {
        summaryLoadingElement.classList.add('hidden');
        contentLoadingElement.classList.add('hidden');
    }
}

async function generatePDF() {
    const hiddenContentElement = document.getElementById('hiddenContent');
    const content = hiddenContentElement.value.trim();
    const images = [];

    if (!content) {
        console.error('Content is empty. Cannot generate PDF.');
        return;
    }

    try {
        const response = await axios.post('/generate_pdf', { title: articleTitle, content: content, images: images }, { responseType: 'blob' });
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
        const response = await axios.post('/query', { content: content, query: query, model: model });
        // Process the response data using marked.js and DOMPurify
        const sanitizedContent = DOMPurify.sanitize(response.data.result);
        queryResultElement.innerHTML = sanitizedContent;
    } catch (error) {
        queryResultElement.textContent = 'Error querying article: ' + (error.response?.data?.error || error.message);
    } finally {
        queryLoadingElement.classList.add('hidden');
    }
}
