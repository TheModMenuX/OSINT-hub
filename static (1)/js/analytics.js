/**
 * Enhanced Seeker Analytics JavaScript
 * Advanced data visualization and analytics dashboard
 */

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.data = {};
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        this.loadAnalyticsData();
        this.setupAutoRefresh();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Export buttons
        document.querySelectorAll('[onclick^="exportData"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const format = e.target.textContent.toLowerCase().includes('csv') ? 'csv' :
                             e.target.textContent.toLowerCase().includes('json') ? 'json' : 'kml';
                this.exportData(format);
            });
        });
        
        // Refresh button
        const refreshBtn = document.querySelector('.btn-outline-primary[onclick="refreshAnalytics()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadAnalyticsData();
            });
        }
    }
    
    async loadAnalyticsData() {
        try {
            const response = await fetch('/api/statistics');
            if (response.ok) {
                this.data = await response.json();
                this.updateCharts();
                this.updateMetrics();
            } else {
                throw new Error('Failed to load analytics data');
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics data');
        }
    }
    
    updateCharts() {
        this.createTemplateChart();
        this.createDailyChart();
        this.createAccuracyChart();
        this.createHourlyChart();
        this.createPlatformChart();
        this.createLanguageChart();
        this.createTimezoneChart();
    }
    
    createTemplateChart() {
        const ctx = document.getElementById('templateChart');
        if (!ctx) return;
        
        const templateStats = this.data.template_stats || {};
        const labels = Object.keys(templateStats);
        const data = Object.values(templateStats);
        
        if (this.charts.template) {
            this.charts.template.destroy();
        }
        
        this.charts.template = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    createDailyChart() {
        const ctx = document.getElementById('dailyChart');
        if (!ctx) return;
        
        const dailyTrend = this.data.time_analytics?.daily_trend || {};
        const labels = Object.keys(dailyTrend).slice(-30); // Last 30 days
        const data = labels.map(date => dailyTrend[date] || 0);
        
        if (this.charts.daily) {
            this.charts.daily.destroy();
        }
        
        this.charts.daily = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.map(date => new Date(date).toLocaleDateString()),
                datasets: [{
                    label: 'Sessions',
                    data: data,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#36A2EB',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    createAccuracyChart() {
        const ctx = document.getElementById('accuracyChart');
        if (!ctx) return;
        
        const accuracyData = this.data.location_analytics?.accuracy_distribution || {};
        const labels = ['Very High (<10m)', 'High (10-50m)', 'Medium (50-100m)', 'Low (>100m)'];
        const data = [
            accuracyData.very_high || 0,
            accuracyData.high || 0,
            accuracyData.medium || 0,
            accuracyData.low || 0
        ];
        
        if (this.charts.accuracy) {
            this.charts.accuracy.destroy();
        }
        
        this.charts.accuracy = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sessions',
                    data: data,
                    backgroundColor: [
                        '#28a745', '#ffc107', '#fd7e14', '#dc3545'
                    ],
                    borderColor: [
                        '#1e7e34', '#e0a800', '#e8590c', '#bd2130'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    createHourlyChart() {
        const ctx = document.getElementById('hourlyChart');
        if (!ctx) return;
        
        const hourlyData = this.data.time_analytics?.hourly_distribution || {};
        const labels = Array.from({length: 24}, (_, i) => `${i.toString().padStart(2, '0')}:00`);
        const data = labels.map((_, hour) => hourlyData[hour.toString()] || 0);
        
        if (this.charts.hourly) {
            this.charts.hourly.destroy();
        }
        
        this.charts.hourly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sessions',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: '#36A2EB',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    createPlatformChart() {
        const ctx = document.getElementById('platformChart');
        if (!ctx) return;
        
        const platformData = this.data.device_analytics?.platform_distribution || {};
        const labels = Object.keys(platformData).slice(0, 5);
        const data = labels.map(platform => platformData[platform]);
        
        if (this.charts.platform) {
            this.charts.platform.destroy();
        }
        
        this.charts.platform = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    createLanguageChart() {
        const ctx = document.getElementById('languageChart');
        if (!ctx) return;
        
        const languageData = this.data.device_analytics?.language_distribution || {};
        const labels = Object.keys(languageData).slice(0, 5);
        const data = labels.map(lang => languageData[lang]);
        
        if (this.charts.language) {
            this.charts.language.destroy();
        }
        
        this.charts.language = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF9F40', '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    createTimezoneChart() {
        const ctx = document.getElementById('timezoneChart');
        if (!ctx) return;
        
        const timezoneData = this.data.device_analytics?.timezone_distribution || {};
        const labels = Object.keys(timezoneData).slice(0, 5);
        const data = labels.map(tz => timezoneData[tz]);
        
        if (this.charts.timezone) {
            this.charts.timezone.destroy();
        }
        
        this.charts.timezone = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#9966FF', '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    updateMetrics() {
        // Update advanced metrics
        const stats = this.data;
        
        document.getElementById('avg-accuracy').textContent = `${stats.avg_accuracy || 0}m`;
        
        // Calculate high accuracy count
        const accuracyDist = stats.location_analytics?.accuracy_distribution || {};
        const highAccuracyCount = (accuracyDist.very_high || 0) + (accuracyDist.high || 0);
        document.getElementById('high-accuracy-count').textContent = highAccuracyCount;
        
        // Mobile percentage (placeholder - would need actual device type data)
        document.getElementById('mobile-percentage').textContent = '85%';
        
        // Unique fingerprints (placeholder - would need actual fingerprint data)
        document.getElementById('unique-fingerprints').textContent = stats.unique_ips || 0;
    }
    
    async exportData(format) {
        try {
            const response = await fetch(`/api/export/${format}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `seeker_data.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showSuccess(`Data exported as ${format.toUpperCase()}`);
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export data');
        }
    }
    
    setupAutoRefresh() {
        // Refresh data every 60 seconds
        this.refreshInterval = setInterval(() => {
            this.loadAnalyticsData();
        }, 60000);
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'danger');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    destroy() {
        // Clean up charts and intervals
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Global export functions (for onclick handlers)
window.exportData = function(format) {
    if (window.analyticsDashboard) {
        window.analyticsDashboard.exportData(format);
    }
};

window.refreshAnalytics = function() {
    if (window.analyticsDashboard) {
        window.analyticsDashboard.loadAnalyticsData();
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsDashboard = new AnalyticsDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.analyticsDashboard) {
        window.analyticsDashboard.destroy();
    }
});
