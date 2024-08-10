let articleTitle = '';

async function fetchArticle() {
    const url = document.getElementById('urlInput').value;
    const errorElement = document.getElementById('error');
    const contentElement = document.getElementById('content');
    const summaryElement = document.getElementById('summary');
    const loadingElement = document.getElementById('loading');
    const articleTitleElement = document.getElementById('articleTitle');
    const summaryLoadingElement = document.getElementById('summaryLoading');
    const contentLoadingElement = document.getElementById('contentLoading');
    const summaryCollapse = document.getElementById('summaryCollapse');

    errorElement.textContent = '';
    contentElement.innerHTML = '';
    summaryElement.innerHTML = '';
    summaryLoadingElement.classList.remove('hidden');
    contentLoadingElement.classList.remove('hidden');

    try {
        const response = await axios.post('/fetch', { url: url });
        const article = response.data.content;
        articleTitle = article.title;

        articleTitleElement.textContent = article.title;

        contentElement.innerHTML = `
            <h3 class="text-xl font-semibold mb-4">Content:</h3>
            <p>${article.content.replace(/\n/g, '<br>')}</p>
        `;
    
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
    const contentElement = document.getElementById('content');
    const content = contentElement.innerText;
    const images = []; // Assuming images are fetched along with the content and stored somewhere

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
    const contentElement = document.getElementById('content');
    const queryResultElement = document.getElementById('queryResult');
    const queryLoadingElement = document.getElementById('queryLoading');
    const content = contentElement.innerText;

    queryResultElement.textContent = '';
    queryLoadingElement.classList.remove('hidden');

    try {
        const response = await axios.post('/query', { content: content, query: query, model: model });
        queryResultElement.textContent = response.data.result;
    } catch (error) {
        queryResultElement.textContent = 'Error querying article: ' + (error.response?.data?.error || error.message);
    } finally {
        queryLoadingElement.classList.add('hidden');
    }
}
