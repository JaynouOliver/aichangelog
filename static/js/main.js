/**
 * AI Changelog Generator Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Markdown rendering for any content with class markdown-content
    document.querySelectorAll('.markdown-content').forEach(element => {
        if (element.innerHTML.trim()) {
            const markdown = element.textContent.trim();
            const html = marked.parse(markdown);
            element.innerHTML = html;
            
            // Apply syntax highlighting
            element.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        }
    });

    // Handle copy buttons if they exist
    const copyButtons = document.querySelectorAll('.copy-btn');
    if (copyButtons.length > 0) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const contentType = this.dataset.content;
                let content;
                
                if (contentType === 'markdown') {
                    content = document.getElementById('markdown-content').textContent;
                } else if (contentType === 'html') {
                    content = document.getElementById('html-content').innerHTML;
                } else {
                    return;
                }
                
                // Copy to clipboard
                navigator.clipboard.writeText(content).then(() => {
                    // Temporary feedback
                    const originalHTML = this.innerHTML;
                    this.innerHTML = '<i class="bi bi-check"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalHTML;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    alert('Failed to copy to clipboard');
                });
            });
        });
    }

    // Repository path autocomplete (local storage)
    const repoPathInput = document.getElementById('repo_path');
    if (repoPathInput) {
        // Load previously used paths
        const savedPaths = JSON.parse(localStorage.getItem('recentRepoPaths') || '[]');
        
        if (savedPaths.length > 0) {
            // Create datalist for autocomplete
            const datalist = document.createElement('datalist');
            datalist.id = 'repo-paths';
            
            savedPaths.forEach(path => {
                const option = document.createElement('option');
                option.value = path;
                datalist.appendChild(option);
            });
            
            document.body.appendChild(datalist);
            repoPathInput.setAttribute('list', 'repo-paths');
        }
        
        // Save path on form submit
        const form = repoPathInput.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                const path = repoPathInput.value.trim();
                if (path) {
                    let paths = JSON.parse(localStorage.getItem('recentRepoPaths') || '[]');
                    // Remove duplicates
                    paths = paths.filter(p => p !== path);
                    // Add to beginning
                    paths.unshift(path);
                    // Keep only last 5
                    paths = paths.slice(0, 5);
                    localStorage.setItem('recentRepoPaths', JSON.stringify(paths));
                }
            });
        }
    }
});
