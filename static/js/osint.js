/**
 * OSINT Search JavaScript functionality
 * Handles search forms, result processing, and UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('OSINT module loaded');
    
    // Initialize OSINT functionality
    initializeOSINT();
    
    // Setup form enhancements
    setupSearchForms();
    
    // Initialize result handlers
    setupResultHandlers();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Initialize tooltips and popovers
    initializeUIComponents();
});

/**
 * Initialize OSINT search functionality
 */
function initializeOSINT() {
    console.log('Initializing OSINT search tools...');
    
    // Add real-time validation to search forms
    const searchInputs = document.querySelectorAll('input[name="username"], input[name="domain"], input[name="email"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateSearchInput(this);
        });
        
        input.addEventListener('paste', function() {
            // Handle paste events with a small delay to get the pasted content
            setTimeout(() => {
                validateSearchInput(this);
                cleanupInput(this);
            }, 10);
        });
    });
    
    // Add loading states to search buttons
    const searchButtons = document.querySelectorAll('button[type="submit"]');
    searchButtons.forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                showSearchLoading(button);
            });
        }
    });
}

/**
 * Setup search form enhancements
 */
function setupSearchForms() {
    const forms = document.querySelectorAll('form[action*="search"]');
    
    forms.forEach(form => {
        // Add form validation
        form.addEventListener('submit', function(e) {
            const input = this.querySelector('input[type="text"], input[type="email"]');
            if (input && !validateSearchInput(input)) {
                e.preventDefault();
                showValidationError(input);
                return false;
            }
        });
        
        // Add enter key handling
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    form.querySelector('button[type="submit"]').click();
                }
            });
        });
    });
}

/**
 * Setup result page handlers
 */
function setupResultHandlers() {
    // If we're on a results page, enhance the display
    if (window.location.pathname.includes('search') && document.querySelector('.card-body pre')) {
        enhanceResults();
    }
    
    // Setup copy to clipboard functionality
    setupCopyButtons();
    
    // Setup result filtering if applicable
    setupResultFiltering();
}

/**
 * Validate search input based on type
 */
function validateSearchInput(input) {
    const value = input.value.trim();
    const inputName = input.name;
    let isValid = false;
    let errorMessage = '';
    
    // Clear previous validation styles
    input.classList.remove('is-invalid', 'is-valid');
    
    if (!value) {
        return false; // Empty input, no validation needed
    }
    
    switch (inputName) {
        case 'username':
            isValid = validateUsername(value);
            errorMessage = 'Username should be 3-30 characters, alphanumeric with dots, dashes, underscores';
            break;
        case 'domain':
            isValid = validateDomain(value);
            errorMessage = 'Please enter a valid domain name (e.g., example.com)';
            break;
        case 'email':
            isValid = validateEmail(value);
            errorMessage = 'Please enter a valid email address';
            break;
    }
    
    // Apply validation styles
    if (isValid) {
        input.classList.add('is-valid');
        hideValidationError(input);
    } else {
        input.classList.add('is-invalid');
        showValidationError(input, errorMessage);
    }
    
    return isValid;
}

/**
 * Username validation
 */
function validateUsername(username) {
    // Username rules: 3-30 characters, alphanumeric, dots, dashes, underscores
    const usernameRegex = /^[a-zA-Z0-9._-]{3,30}$/;
    return usernameRegex.test(username);
}

/**
 * Domain validation
 */
function validateDomain(domain) {
    // Remove protocol if present
    domain = domain.replace(/^https?:\/\//, '');
    
    // Basic domain validation
    const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
    return domainRegex.test(domain) && domain.length <= 253;
}

/**
 * Email validation
 */
function validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

/**
 * Show validation error
 */
function showValidationError(input, message = '') {
    let errorElement = input.parentNode.querySelector('.invalid-feedback');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        input.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

/**
 * Hide validation error
 */
function hideValidationError(input) {
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

/**
 * Show loading state for search button
 */
function showSearchLoading(button) {
    const originalText = button.innerHTML;
    const searchType = getSearchType();
    
    button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>Searching ${searchType}...`;
    button.disabled = true;
    
    // Store original text to restore if needed
    button.dataset.originalText = originalText;
}

/**
 * Get search type from current page
 */
function getSearchType() {
    const path = window.location.pathname;
    if (path.includes('username')) return 'Username';
    if (path.includes('domain')) return 'Domain';
    if (path.includes('email')) return 'Email';
    return 'Target';
}

/**
 * Clean up input (remove extra spaces, convert to lowercase for certain types)
 */
function cleanupInput(input) {
    let value = input.value.trim();
    
    switch (input.name) {
        case 'username':
            // Remove @ symbol if present
            value = value.replace(/^@/, '');
            break;
        case 'domain':
            // Remove protocol and trailing slash
            value = value.replace(/^https?:\/\//, '').replace(/\/$/, '');
            value = value.toLowerCase();
            break;
        case 'email':
            value = value.toLowerCase();
            break;
    }
    
    input.value = value;
}

/**
 * Enhance results display
 */
function enhanceResults() {
    // Add syntax highlighting to JSON results
    const preElements = document.querySelectorAll('pre code');
    preElements.forEach(pre => {
        try {
            const content = pre.textContent;
            const jsonData = JSON.parse(content);
            pre.innerHTML = syntaxHighlightJSON(jsonData);
        } catch (e) {
            // Not JSON, leave as is
            console.log('Content is not JSON, skipping syntax highlighting');
        }
    });
    
    // Add expand/collapse for long content
    const longPreElements = document.querySelectorAll('pre');
    longPreElements.forEach(pre => {
        if (pre.scrollHeight > 300) {
            addExpandCollapse(pre);
        }
    });
    
    // Add result statistics
    addResultStatistics();
}

/**
 * Add syntax highlighting to JSON
 */
function syntaxHighlightJSON(json) {
    if (typeof json !== 'string') {
        json = JSON.stringify(json, null, 2);
    }
    
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        let cls = 'text-info'; // numbers
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'text-warning'; // keys
            } else {
                cls = 'text-success'; // strings
            }
        } else if (/true|false/.test(match)) {
            cls = 'text-primary'; // booleans
        } else if (/null/.test(match)) {
            cls = 'text-muted'; // null
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

/**
 * Add expand/collapse functionality
 */
function addExpandCollapse(element) {
    element.style.maxHeight = '300px';
    element.style.overflow = 'hidden';
    element.style.position = 'relative';
    
    const expandButton = document.createElement('button');
    expandButton.className = 'btn btn-outline-secondary btn-sm mt-2';
    expandButton.innerHTML = '<i class="fas fa-expand-alt me-1"></i>Show More';
    expandButton.style.position = 'absolute';
    expandButton.style.bottom = '10px';
    expandButton.style.right = '10px';
    
    let isExpanded = false;
    
    expandButton.addEventListener('click', function() {
        if (isExpanded) {
            element.style.maxHeight = '300px';
            element.style.overflow = 'hidden';
            expandButton.innerHTML = '<i class="fas fa-expand-alt me-1"></i>Show More';
            isExpanded = false;
        } else {
            element.style.maxHeight = 'none';
            element.style.overflow = 'visible';
            expandButton.innerHTML = '<i class="fas fa-compress-alt me-1"></i>Show Less';
            isExpanded = true;
        }
    });
    
    element.appendChild(expandButton);
}

/**
 * Setup copy to clipboard buttons
 */
function setupCopyButtons() {
    const codeElements = document.querySelectorAll('pre code, code');
    
    codeElements.forEach(code => {
        if (code.textContent.length > 20) { // Only add copy button for substantial content
            addCopyButton(code);
        }
    });
}

/**
 * Add copy button to code element
 */
function addCopyButton(codeElement) {
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    
    const copyButton = document.createElement('button');
    copyButton.className = 'btn btn-outline-secondary btn-sm';
    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
    copyButton.style.position = 'absolute';
    copyButton.style.top = '5px';
    copyButton.style.right = '5px';
    copyButton.style.zIndex = '1000';
    copyButton.title = 'Copy to clipboard';
    
    copyButton.addEventListener('click', function() {
        copyToClipboard(codeElement.textContent);
        
        // Visual feedback
        copyButton.innerHTML = '<i class="fas fa-check text-success"></i>';
        setTimeout(() => {
            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        }, 2000);
    });
    
    // Wrap the code element
    codeElement.parentNode.insertBefore(wrapper, codeElement);
    wrapper.appendChild(codeElement);
    wrapper.appendChild(copyButton);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Could not copy text: ', err);
        }
        
        textArea.remove();
    }
}

/**
 * Setup result filtering
 */
function setupResultFiltering() {
    const filterInputs = document.querySelectorAll('input[placeholder*="filter"], input[placeholder*="search"]');
    
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            filterResults(this.value);
        });
    });
}

/**
 * Filter results based on search term
 */
function filterResults(searchTerm) {
    const resultItems = document.querySelectorAll('.card-body .row > div, .list-group-item');
    
    resultItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        const matches = text.includes(searchTerm.toLowerCase());
        
        item.style.display = matches ? 'block' : 'none';
    });
}

/**
 * Add result statistics
 */
function addResultStatistics() {
    const resultCards = document.querySelectorAll('.card .card-body');
    
    resultCards.forEach(card => {
        const items = card.querySelectorAll('.row > div, .list-group-item, li');
        if (items.length > 5) {
            const statsElement = document.createElement('div');
            statsElement.className = 'alert alert-info mt-3';
            statsElement.innerHTML = `<i class="fas fa-info-circle me-2"></i>Total items: ${items.length}`;
            card.appendChild(statsElement);
        }
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Focus search input with '/' key
        if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            const target = e.target;
            if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                const searchInput = document.querySelector('input[name="username"], input[name="domain"], input[name="email"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[name="username"], input[name="domain"], input[name="email"]');
            if (searchInput && searchInput === document.activeElement) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
        
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const form = document.querySelector('form[action*="search"]');
            if (form) {
                e.preventDefault();
                form.submit();
            }
        }
    });
}

/**
 * Initialize UI components
 */
function initializeUIComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show progress indicator for long-running searches
 */
function showSearchProgress(estimatedTime = 30000) {
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container mt-3';
    progressContainer.innerHTML = `
        <div class="alert alert-info">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div>
                    <strong>Search in progress...</strong>
                    <div class="small text-muted">This may take up to ${Math.ceil(estimatedTime / 1000)} seconds</div>
                </div>
            </div>
            <div class="progress mt-2" style="height: 4px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 0%"></div>
            </div>
        </div>
    `;
    
    const form = document.querySelector('form[action*="search"]');
    if (form) {
        form.appendChild(progressContainer);
        
        // Animate progress bar
        const progressBar = progressContainer.querySelector('.progress-bar');
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90; // Don't complete until actual completion
            progressBar.style.width = progress + '%';
        }, 1000);
        
        // Clean up on page unload
        window.addEventListener('beforeunload', () => {
            clearInterval(interval);
        });
    }
}

// Global functions for template usage
window.osintUtils = {
    validateSearchInput,
    cleanupInput,
    copyToClipboard,
    filterResults,
    showSearchProgress
};

// Export functions if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateUsername,
        validateDomain,
        validateEmail,
        copyToClipboard,
        syntaxHighlightJSON
    };
}
