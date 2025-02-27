/* static/js/scripts.js */
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    
    // Check for saved theme preference or use default (dark)
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.toggle('dark-theme', savedTheme === 'dark');
    
    // Set initial toggle state
    if (themeToggle) {
        themeToggle.checked = savedTheme === 'dark';
        
        // Theme toggle handler
        themeToggle.addEventListener('change', function() {
            const isDark = this.checked;
            document.body.classList.toggle('dark-theme', isDark);
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
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
    const yearSpans = document.querySelectorAll('.current-year');
    if (yearSpans.length > 0) {
        const currentYear = new Date().getFullYear();
        yearSpans.forEach(span => {
            span.textContent = currentYear;
        });
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
    
    // FAQ Accordion functionality
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const toggle = item.querySelector('.faq-toggle');
        
        // Hide all answers initially
        answer.style.display = 'none';
        
        question.addEventListener('click', () => {
            // Toggle the display of the answer
            if (answer.style.display === 'none') {
                answer.style.display = 'block';
                toggle.textContent = '−';
                question.classList.add('active');
            } else {
                answer.style.display = 'none';
                toggle.textContent = '+';
                question.classList.remove('active');
            }
        });
    });
});