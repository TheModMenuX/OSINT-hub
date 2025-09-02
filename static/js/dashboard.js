/**
 * Dashboard JavaScript functionality
 * Handles dashboard interactions, real-time updates, and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Update last updated timestamp
    updateLastUpdatedTime();
    
    // Set up periodic updates
    setUpPeriodicUpdates();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add loading states to action buttons
    setupActionButtons();
});

/**
 * Initialize dashboard functionality
 */
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Add smooth transitions to stat cards
    const statCards = document.querySelectorAll('.card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.2s ease-in-out';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add click analytics to quick action buttons
    const actionButtons = document.querySelectorAll('.btn[href*="search"], .btn[href*="create"]');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.textContent.trim();
            console.log(`Dashboard action clicked: ${action}`);
            
            // Add visual feedback
            this.classList.add('loading');
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>' + action;
            
            // Remove loading state after a short delay (form will redirect anyway)
            setTimeout(() => {
                this.classList.remove('loading');
                // Note: this might not execute due to page redirect
            }, 1000);
        });
    });
    
    // System status checks
    checkSystemStatus();
}

/**
 * Update the last updated timestamp
 */
function updateLastUpdatedTime() {
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour12: true,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        lastUpdatedElement.textContent = timeString;
    }
}

/**
 * Set up periodic updates for dashboard data
 */
function setUpPeriodicUpdates() {
    // Update timestamp every second
    setInterval(updateLastUpdatedTime, 1000);
    
    // Optionally refresh dashboard stats periodically (disabled by default)
    // Uncomment the following lines to enable auto-refresh every 5 minutes
    /*
    setInterval(() => {
        console.log('Auto-refreshing dashboard...');
        location.reload();
    }, 5 * 60 * 1000); // 5 minutes
    */
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup action buttons with enhanced interactions
 */
function setupActionButtons() {
    const quickActionButtons = document.querySelectorAll('.btn-lg[href*="search"], .btn-lg[href*="create"]');
    
    quickActionButtons.forEach(button => {
        // Add keyboard navigation
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
        
        // Add focus styles
        button.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 0 0.2rem rgba(88, 166, 255, 0.25)';
        });
        
        button.addEventListener('blur', function() {
            this.style.boxShadow = '';
        });
    });
}

/**
 * Check system status indicators
 */
function checkSystemStatus() {
    const statusIndicators = document.querySelectorAll('.badge.bg-success');
    
    statusIndicators.forEach(indicator => {
        // Add a subtle animation to show they're "active"
        setInterval(() => {
            indicator.style.opacity = '0.7';
            setTimeout(() => {
                indicator.style.opacity = '1';
            }, 200);
        }, 3000 + Math.random() * 2000); // Random interval between 3-5 seconds
    });
}

/**
 * Utility function to format numbers with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Utility function to animate counting up to a number
 */
function animateCounter(element, target, duration = 1000) {
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16); // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

/**
 * Handle search result navigation from dashboard
 */
function navigateToSearch(searchType) {
    const searchUrls = {
        'username': '/osint/username',
        'domain': '/osint/domain',
        'email': '/osint/email'
    };
    
    if (searchUrls[searchType]) {
        window.location.href = searchUrls[searchType];
    }
}

/**
 * Export dashboard data (if needed)
 */
function exportDashboardData() {
    const dashboardData = {
        timestamp: new Date().toISOString(),
        stats: {
            // Collect current dashboard statistics
            totalSearches: document.querySelector('.card-body h3')?.textContent || '0',
            // Add more stats as needed
        }
    };
    
    const dataStr = JSON.stringify(dashboardData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `dashboard_data_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + number keys for quick navigation
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey) {
        switch(e.key) {
            case '1':
                e.preventDefault();
                navigateToSearch('username');
                break;
            case '2':
                e.preventDefault();
                navigateToSearch('domain');
                break;
            case '3':
                e.preventDefault();
                navigateToSearch('email');
                break;
            case '4':
                e.preventDefault();
                window.location.href = '/phishing/create';
                break;
        }
    }
    
    // 'r' key to refresh dashboard
    if (e.key === 'r' && !e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey) {
        const target = e.target;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            location.reload();
        }
    }
});

/**
 * Initialize dashboard animations on load
 */
function initializeDashboardAnimations() {
    // Animate statistics cards on page load
    const statNumbers = document.querySelectorAll('.card-body h3');
    statNumbers.forEach((element, index) => {
        const target = parseInt(element.textContent) || 0;
        element.textContent = '0';
        
        // Stagger the animations
        setTimeout(() => {
            animateCounter(element, target, 1500);
        }, index * 200);
    });
}

// Initialize animations when page is fully loaded
window.addEventListener('load', function() {
    setTimeout(initializeDashboardAnimations, 300);
});

// Global functions for inline event handlers (if needed)
window.dashboardUtils = {
    navigateToSearch,
    exportDashboardData,
    formatNumber,
    animateCounter
};
