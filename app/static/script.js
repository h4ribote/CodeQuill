document.addEventListener('DOMContentLoaded', () => {
    const codeBlocks = document.querySelectorAll('pre');

    codeBlocks.forEach(block => {
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = 'Copy';

        block.appendChild(copyButton);

        copyButton.addEventListener('click', () => {
            const code = block.querySelector('code');
            if (code) {
                navigator.clipboard.writeText(code.innerText).then(() => {
                    copyButton.textContent = 'Copied!';
                    setTimeout(() => {
                        copyButton.textContent = 'Copy';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                    copyButton.textContent = 'Error';
                });
            }
        });
    });

    const relatedArticlesSection = document.querySelector('.related-articles');
    if (relatedArticlesSection && window.location.pathname.includes('/articles/')) {
        const pathParts = window.location.pathname.split('/');
        const articleId = pathParts[pathParts.length - 1];
        
        if (articleId) {
            fetch(`/api/articles/${articleId}/related/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(articles => {
                    const listElement = document.getElementById('related-articles-list');
                    if (articles.length > 0) {
                        listElement.innerHTML = '';
                        articles.forEach(article => {
                            const li = document.createElement('li');
                            const a = document.createElement('a');
                            a.href = `/articles/${article.id}`;
                            a.textContent = article.title;
                            li.appendChild(a);
                            listElement.appendChild(li);
                        });
                    } else {
                        relatedArticlesSection.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Failed to fetch related articles:', error);
                    relatedArticlesSection.style.display = 'none';
                });
        }
    }
});
