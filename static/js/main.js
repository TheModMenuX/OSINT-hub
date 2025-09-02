/* OSINT Intelligence Platform - Main JavaScript */

// Global variables
let searchInProgress = false;
let searchTimeout;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🔍 OSINT Platform initialized');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidation();
    
    // Initialize search functionality
    initializeSearchHandlers();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize theme handlers
    initializeThemeHandlers();
    
    // Initialize notification system
    initializeNotifications();
    
    // Initialize clipboard functionality
    initializeClipboard();
    
    // Add loading states to forms
    initializeLoadingStates();
    
    // Initialize auto-save for forms
    initializeAutoSave();
    
    // Initialize dark mode persistence
    initializeDarkMode();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Enhanced form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            
            form.classList.add('was-validated');
        }, false);
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    if (field.checkValidity()) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
}

/**
 * Initialize search handlers with enhanced UX
 */
function initializeSearchHandlers() {
    const searchForms = document.querySelectorAll('form[method="POST"]');
    
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !form.classList.contains('was-validated') || form.checkValidity()) {
                showSearchProgress(submitBtn);
            }
        });
    });
}

/**
 * Show search progress with enhanced UX
 */
function showSearchProgress(button) {
    if (searchInProgress) return;
    
    searchInProgress = true;
    const originalText = button.innerHTML;
    const loadingText = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    
    button.innerHTML = loadingText;
    button.disabled = true;
    button.classList.add('scanning');
    
    // Add progress bar if not exists
    let progressBar = document.querySelector('.search-progress');
    if (!progressBar) {
        progressBar = document.createElement('div');
        progressBar.className = 'progress mt-3 search-progress';
        progressBar.innerHTML = '<div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>';
        button.parentNode.appendChild(progressBar);
    }
    
    // Animate progress
    animateProgress(progressBar.querySelector('.progress-bar'));
    
    // Reset after timeout (fallback)
    searchTimeout = setTimeout(() => {
        resetSearchProgress(button, originalText, progressBar);
    }, 30000);
}

/**
 * Animate progress bar
 */
function animateProgress(progressBar) {
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += Math.random() * 10;
            progressBar.style.width = Math.min(width, 90) + '%';
        }
    }, 500);
}

/**
 * Reset search progress
 */
function resetSearchProgress(button, originalText, progressBar) {
    searchInProgress = false;
    button.innerHTML = originalText;
    button.disabled = false;
    button.classList.remove('scanning');
    
    if (progressBar) {
        progressBar.remove();
    }
    
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+/ or Cmd+/ - Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="text"], input[type="email"], input[type="tel"]');
            if (searchInput) {
                searchInput.focus();
                showNotification('Search focused', 'info');
            }
        }
        
        // Escape - Clear focus and close modals
        if (e.key === 'Escape') {
            document.activeElement.blur();
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });
        }
        
        // Ctrl+Enter - Submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const form = document.querySelector('form:not([data-no-shortcut])');
            if (form) {
                form.requestSubmit();
            }
        }
    });
}

/**
 * Initialize theme handlers
 */
function initializeThemeHandlers() {
    // Add theme toggle if needed
    const themeToggle = document.querySelector('#theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('osint-theme', newTheme);
            showNotification(`Switched to ${newTheme} theme`, 'info');
        });
    }
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Create notification container if not exists
    if (!document.querySelector('.notification-container')) {
        const container = document.createElement('div');
        container.className = 'notification-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.querySelector('.notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // Auto-dismiss
    setTimeout(() => {
        if (notification.parentNode) {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }
    }, duration);
}

/**
 * Get icon for notification type
 */
function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'info': 'info-circle',
        'warning': 'exclamation-triangle',
        'danger': 'exclamation-circle',
        'error': 'exclamation-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Initialize clipboard functionality
 */
function initializeClipboard() {
    // Add click-to-copy functionality to code blocks
    const codeBlocks = document.querySelectorAll('pre code, code');
    codeBlocks.forEach(block => {
        if (block.textContent.length > 10) {
            block.style.cursor = 'pointer';
            block.title = 'Click to copy';
            
            block.addEventListener('click', function() {
                copyToClipboard(this.textContent.trim());
            });
        }
    });
    
    // Add copy buttons to results
    const resultCards = document.querySelectorAll('.card-body');
    resultCards.forEach(card => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-outline-secondary btn-sm position-absolute top-0 end-0 m-2';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy results';
        copyBtn.style.zIndex = '10';
        
        if (card.style.position !== 'relative') {
            card.style.position = 'relative';
        }
        
        copyBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const text = extractTextFromElement(card);
            copyToClipboard(text);
        });
        
        card.appendChild(copyBtn);
    });
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard', 'success', 2000);
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showNotification('Copied to clipboard', 'success', 2000);
        } catch (fallbackErr) {
            showNotification('Failed to copy', 'error', 2000);
        }
        
        document.body.removeChild(textArea);
    }
}

/**
 * Extract clean text from element
 */
function extractTextFromElement(element) {
    const clone = element.cloneNode(true);
    // Remove buttons and non-essential elements
    const buttons = clone.querySelectorAll('button, .btn');
    buttons.forEach(btn => btn.remove());
    
    return clone.textContent.trim().replace(/\s+/g, ' ');
}

/**
 * Initialize loading states
 */
function initializeLoadingStates() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('glow');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('glow');
        });
    });
}

/**
 * Initialize auto-save functionality for forms
 */
function initializeAutoSave() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            // Load saved value
            const savedValue = localStorage.getItem(`osint-form-${input.name || input.id}`);
            if (savedValue && input.type !== 'password') {
                input.value = savedValue;
            }
            
            // Save on input
            input.addEventListener('input', function() {
                if (this.type !== 'password' && (this.name || this.id)) {
                    localStorage.setItem(`osint-form-${this.name || this.id}`, this.value);
                }
            });
        });
        
        // Clear saved values on successful submit
        form.addEventListener('submit', function() {
            if (this.checkValidity()) {
                const inputs = this.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    if (input.name || input.id) {
                        localStorage.removeItem(`osint-form-${input.name || input.id}`);
                    }
                });
            }
        });
    });
}

/**
 * Initialize dark mode persistence
 */
function initializeDarkMode() {
    const savedTheme = localStorage.getItem('osint-theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
    }
}

/**
 * Utility function to format timestamps
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
        return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
        return `${Math.floor(diff / 60000)} minutes ago`;
    } else if (diff < 86400000) { // Less than 1 day
        return `${Math.floor(diff / 3600000)} hours ago`;
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Utility function to validate IP address
 */
function isValidIP(ip) {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
}

/**
 * Utility function to validate email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Utility function to validate domain
 */
function isValidDomain(domain) {
    const domainRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
    return domainRegex.test(domain);
}

/**
 * Enhanced search functionality with suggestions
 */
function initializeSearchSuggestions() {
    const searchInputs = document.querySelectorAll('input[type="text"]:not([data-no-suggestions])');
    
    searchInputs.forEach(input => {
        let suggestionTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(suggestionTimeout);
            suggestionTimeout = setTimeout(() => {
                showSearchSuggestions(this);
            }, 300);
        });
        
        input.addEventListener('blur', function() {
            setTimeout(() => {
                hideSuggestions(this);
            }, 200);
        });
    });
}

/**
 * Show search suggestions
 */
function showSearchSuggestions(input) {
    const value = input.value.trim();
    if (value.length < 2) {
        hideSuggestions(input);
        return;
    }
    
    let suggestions = [];
    
    // Generate suggestions based on input type and value
    if (input.name === 'ip_address') {
        if (isValidIP(value)) {
            suggestions = ['Analyze this IP address'];
        } else {
            suggestions = ['8.8.8.8', '1.1.1.1', '208.67.222.222'];
        }
    } else if (input.name === 'email') {
        if (value.includes('@')) {
            suggestions = ['Validate this email', 'Check for breaches'];
        } else {
            suggestions = [`${value}@gmail.com`, `${value}@yahoo.com`, `${value}@outlook.com`];
        }
    } else if (input.name === 'domain') {
        suggestions = [`${value}.com`, `${value}.org`, `${value}.net`];
    } else if (input.name === 'username') {
        suggestions = ['Search across all platforms', 'Check social media'];
    }
    
    displaySuggestions(input, suggestions);
}

/**
 * Display suggestions dropdown
 */
function displaySuggestions(input, suggestions) {
    hideSuggestions(input);
    
    if (suggestions.length === 0) return;
    
    const dropdown = document.createElement('div');
    dropdown.className = 'suggestion-dropdown position-absolute bg-dark border border-secondary rounded mt-1 w-100';
    dropdown.style.zIndex = '1000';
    dropdown.style.maxHeight = '200px';
    dropdown.style.overflowY = 'auto';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item p-2 text-light cursor-pointer';
        item.textContent = suggestion;
        item.style.cursor = 'pointer';
        
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(255, 193, 7, 0.1)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
        
        item.addEventListener('click', function() {
            input.value = suggestion;
            hideSuggestions(input);
            input.focus();
        });
        
        dropdown.appendChild(item);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(dropdown);
}

/**
 * Hide suggestions dropdown
 */
function hideSuggestions(input) {
    const existing = input.parentNode.querySelector('.suggestion-dropdown');
    if (existing) {
        existing.remove();
    }
}

/**
 * Initialize result animations
 */
function initializeResultAnimations() {
    const results = document.querySelectorAll('.fade-in');
    results.forEach((result, index) => {
        result.style.animationDelay = `${index * 0.1}s`;
    });
}

/**
 * Export functionality enhancement
 */
function enhancedExport(data, filename, format = 'json') {
    let content, mimeType, extension;
    
    switch (format.toLowerCase()) {
        case 'csv':
            content = convertToCSV(data);
            mimeType = 'text/csv';
            extension = 'csv';
            break;
        case 'txt':
            content = convertToText(data);
            mimeType = 'text/plain';
            extension = 'txt';
            break;
        default:
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
            extension = 'json';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = `${filename}.${extension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showNotification(`Results exported as ${extension.toUpperCase()}`, 'success');
}

/**
 * Convert data to CSV format
 */
function convertToCSV(data) {
    // Simple CSV conversion - can be enhanced based on data structure
    const headers = Object.keys(data).join(',');
    const values = Object.values(data).map(val => 
        typeof val === 'object' ? JSON.stringify(val) : val
    ).join(',');
    
    return `${headers}\n${values}`;
}

/**
 * Convert data to readable text format
 */
function convertToText(data) {
    let text = '';
    
    function processObject(obj, indent = 0) {
        const spaces = ' '.repeat(indent);
        for (const [key, value] of Object.entries(obj)) {
            if (typeof value === 'object' && value !== null) {
                text += `${spaces}${key}:\n`;
                processObject(value, indent + 2);
            } else {
                text += `${spaces}${key}: ${value}\n`;
            }
        }
    }
    
    processObject(data);
    return text;
}

// Initialize additional functionality when needed
setTimeout(() => {
    initializeSearchSuggestions();
    initializeResultAnimations();
}, 1000);

// Global error handler
window.addEventListener('error', function(e) {
    console.error('OSINT Platform Error:', e.error);
    showNotification('An unexpected error occurred', 'error');
});

// Prevent form resubmission on refresh
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

console.log('🎯 OSINT Platform fully loaded and ready');
