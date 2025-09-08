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
});
