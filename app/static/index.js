document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');
    const searchForm = document.getElementById('search-form');
    const searchQuery = document.getElementById('search-query');
    const searchResults = document.getElementById('search-results');
    const recommendedList = document.getElementById('recommended-articles');
    const randomList = document.getElementById('random-articles');

    const API_BASE_URL = window.location.origin;

    const renderArticleList = (element, articles) => {
        element.innerHTML = '';
        if (articles.length === 0) {
            element.innerHTML = '<li>No articles found.</li>';
            return;
        }
        articles.forEach(article => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            const viewUrl = `/${article.file_path.replace('static/', '')}`;
            a.href = viewUrl;
            a.textContent = article.title;
            a.target = "_blank";
            li.appendChild(a);
            element.appendChild(li);
        });
    };

    const fetchRecommendedArticles = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/articles/recommended/`);
            if (!response.ok) throw new Error('Network response was not ok');
            const articles = await response.json();
            renderArticleList(recommendedList, articles);
        } catch (error) {
            console.error('Failed to fetch recommended articles:', error);
            recommendedList.innerHTML = '<li>Error loading articles.</li>';
        }
    };

    const fetchRandomArticles = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/articles/random/`);
            if (!response.ok) throw new Error('Network response was not ok');
            const articles = await response.json();
            renderArticleList(randomList, articles);
        } catch (error) {
            console.error('Failed to fetch random articles:', error);
            randomList.innerHTML = '<li>Error loading articles.</li>';
        }
    };

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        uploadStatus.textContent = 'Uploading...';
        const formData = new FormData(uploadForm);
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/articles/`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                uploadStatus.textContent = 'Upload successful!';
                uploadStatus.style.color = 'green';
                uploadForm.reset();
                fetchRecommendedArticles();
                fetchRandomArticles();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }
        } catch (error) {
            uploadStatus.textContent = `Error: ${error.message}`;
            uploadStatus.style.color = 'red';
            console.error('Upload failed:', error);
        }
    });

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchQuery.value.trim();
        if (!query) return;

        try {
            const response = await fetch(`${API_BASE_URL}/api/articles/search/?query=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const articles = await response.json();
            renderArticleList(searchResults, articles);
        } catch (error) {
            console.error('Failed to perform search:', error);
            searchResults.innerHTML = '<li>Error performing search.</li>';
        }
    });

    fetchRecommendedArticles();
    fetchRandomArticles();
});
