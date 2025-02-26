/* static/js/scripts.js */
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    
    // Check for saved theme preference or use default (dark)
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.toggle('dark-theme', savedTheme === 'dark');
    updateThemeIcon(savedTheme === 'dark');
    
    // Theme toggle button handler
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDark = document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateThemeIcon(isDark);
        });
    }
    
    function updateThemeIcon(isDark) {
        if (themeToggle) {
            themeToggle.textContent = isDark ? '☀️' : '🌙';
            themeToggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
        }
    }
    
    // File input handling
    const fileInput = document.getElementById('file');
    if (fileInput) {
        const fileLabel = document.querySelector('.file-label');
        const originalText = fileLabel.textContent;
        
        fileInput.addEventListener('change', function(e) {
            if (this.files && this.files.length > 0) {
                const fileName = this.files[0].name;
                fileLabel.textContent = fileName;
                
                // Validate file size
                const fileSize = this.files[0].size / 1024 / 1024; // Size in MB
                const maxSize = parseFloat(document.querySelector('.file-limits').textContent.match(/\d+(\.\d+)?/)[0]);
                
                if (fileSize > maxSize) {
                    alert(`File is too large. Maximum allowed size is ${maxSize}MB.`);
                    this.value = '';
                    fileLabel.textContent = originalText;
                }
            } else {
                fileLabel.textContent = originalText;
            }
        });
        
        // Drag and drop support
        const dropZone = document.querySelector('.file-input label');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, function(e) {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        // Add visual cues for drag events
        dropZone.addEventListener('dragenter', function() {
            this.style.backgroundColor = 'rgba(76, 175, 80, 0.1)';
            this.style.borderColor = '#4CAF50';
        });
        
        dropZone.addEventListener('dragover', function() {
            this.style.backgroundColor = 'rgba(76, 175, 80, 0.1)';
            this.style.borderColor = '#4CAF50';
        });
        
        dropZone.addEventListener('dragleave', function() {
            this.style.backgroundColor = '';
            this.style.borderColor = '';
        });
        
        dropZone.addEventListener('drop', function(e) {
            this.style.backgroundColor = '';
            this.style.borderColor = '';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                
                // Trigger change event to update the label
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        });
    }
    
    // Add current year to footer
    const footerYear = document.querySelector('footer p');
    if (footerYear) {
        const currentYear = new Date().getFullYear();
        footerYear.innerHTML = footerYear.innerHTML.replace('{{ current_year }}', currentYear);
    }
    
    // Auto hide error and success messages after a few seconds
    const messages = document.querySelectorAll('.error-message, .success-message');
    messages.forEach(message => {
        setTimeout(() => {
            if (message.classList.contains('error-message') || message.classList.contains('success-message')) {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 500);
            }
        }, 5000);
    });
});