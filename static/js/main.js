/**
 * OSINT Tools - Cyber Intelligence Platform
 * Main JavaScript file for interactive elements and animations
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔮 OSINT Tools - Cyber Interface Initialized');
    
    // Initialize all components
    initializeMatrixBackground();
    initializeCyberEffects();
    initializeFormEnhancements();
    initializeAnimations();
    initializeTooltips();
    initializeParticleEffects();
});

/**
 * Matrix Background Animation
 */
function initializeMatrixBackground() {
    const matrixBg = document.getElementById('matrix-bg');
    if (!matrixBg) return;

    // Create canvas for matrix effect
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.1';
    canvas.style.pointerEvents = 'none';
    
    matrixBg.appendChild(canvas);

    // Matrix characters
    const matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}";
    const matrixArray = matrix.split("");

    let font_size = 14;
    let columns = 0;
    let drops = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        columns = canvas.width / font_size;
        
        // Reset drops array
        drops = [];
        for(let x = 0; x < columns; x++) {
            drops[x] = 1;
        }
    }

    function drawMatrix() {
        // Semi-transparent black background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Green text
        ctx.fillStyle = '#00ff00';
        ctx.font = font_size + 'px monospace';

        for(let i = 0; i < drops.length; i++) {
            const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
            ctx.fillText(text, i * font_size, drops[i] * font_size);

            if(drops[i] * font_size > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    // Initialize canvas
    resizeCanvas();
    
    // Start matrix animation
    setInterval(drawMatrix, 35);
    
    // Handle window resize
    window.addEventListener('resize', resizeCanvas);
}

/**
 * Cyber Effects - Glowing and hover animations
 */
function initializeCyberEffects() {
    // Add glow effect to important elements
    const glowElements = document.querySelectorAll('.cyber-btn, .cyber-brand, .cyber-icon, .stat-number');
    
    glowElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.filter = 'drop-shadow(0 0 10px currentColor)';
            this.style.transform = 'scale(1.05)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.filter = '';
            this.style.transform = '';
        });
    });

    // Cyber typing effect for headers
    const typeElements = document.querySelectorAll('h1, h2');
    typeElements.forEach(element => {
        if (element.dataset.typed !== 'true') {
            typeWriterEffect(element);
            element.dataset.typed = 'true';
        }
    });

    // Add scanning line effect to cards
    addScanningEffect();

    // Initialize cyber grid effects
    initializeCyberGrid();
}

/**
 * Typewriter Effect
 */
function typeWriterEffect(element) {
    const text = element.textContent;
    element.textContent = '';
    element.style.borderRight = '2px solid #00ffff';
    
    let i = 0;
    const timer = setInterval(() => {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
        } else {
            clearInterval(timer);
            // Remove cursor after typing
            setTimeout(() => {
                element.style.borderRight = 'none';
            }, 1000);
        }
    }, 50);
}

/**
 * Scanning Line Effect
 */
function addScanningEffect() {
    const cards = document.querySelectorAll('.cyber-card, .info-card, .stat-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (!this.querySelector('.scan-line')) {
                const scanLine = document.createElement('div');
                scanLine.className = 'scan-line';
                scanLine.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 2px;
                    background: linear-gradient(90deg, transparent, #00ffff, transparent);
                    animation: scan 1.5s ease-in-out;
                    z-index: 10;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(scanLine);
                
                // Remove scan line after animation
                setTimeout(() => {
                    if (scanLine.parentNode) {
                        scanLine.parentNode.removeChild(scanLine);
                    }
                }, 1500);
            }
        });
    });

    // Add CSS for scan animation
    if (!document.querySelector('#scan-style')) {
        const style = document.createElement('style');
        style.id = 'scan-style';
        style.textContent = `
            @keyframes scan {
                0% { left: -100%; }
                100% { left: 100%; }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Cyber Grid Effect
 */
function initializeCyberGrid() {
    const body = document.body;
    
    // Create grid overlay
    const gridOverlay = document.createElement('div');
    gridOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: -2;
        opacity: 0.5;
    `;
    
    body.appendChild(gridOverlay);
}

/**
 * Form Enhancements
 */
function initializeFormEnhancements() {
    // Add focus effects to inputs
    const inputs = document.querySelectorAll('.cyber-input');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.boxShadow = '0 0 15px rgba(0, 255, 255, 0.3)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.boxShadow = '';
        });

        // Add typing sound effect (visual)
        input.addEventListener('input', function() {
            this.style.borderColor = '#00ff00';
            setTimeout(() => {
                this.style.borderColor = '';
            }, 200);
        });
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#ff0040';
                    input.style.boxShadow = '0 0 10px rgba(255, 0, 64, 0.5)';
                    
                    // Show error message
                    showCyberMessage('Please fill in all required fields', 'error');
                } else {
                    input.style.borderColor = '';
                    input.style.boxShadow = '';
                }
            });

            if (!isValid) {
                e.preventDefault();
            } else {
                // Show loading state
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                    submitBtn.disabled = true;
                    
                    // Re-enable after a delay (in case form doesn't redirect)
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 5000);
                }
            }
        });
    });
}

/**
 * Animations and Transitions
 */
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe cards and important elements
    const animatedElements = document.querySelectorAll('.cyber-card, .stat-card, .info-card');
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(el);
    });

    // Parallax effect for hero section
    const heroSection = document.querySelector('.cyber-hero');
    if (heroSection) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.5;
            heroSection.style.transform = `translateY(${parallax}px)`;
        });
    }

    // Floating animation for icons
    const icons = document.querySelectorAll('.cyber-icon');
    icons.forEach((icon, index) => {
        icon.style.animation = `float 3s ease-in-out infinite ${index * 0.5}s`;
    });

    // Add floating animation CSS
    if (!document.querySelector('#float-style')) {
        const style = document.createElement('style');
        style.id = 'float-style';
        style.textContent = `
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Tooltips
 */
function initializeTooltips() {
    // Create custom cyber tooltips
    const elementsWithTooltips = document.querySelectorAll('[title]');
    
    elementsWithTooltips.forEach(element => {
        const tooltipText = element.getAttribute('title');
        element.removeAttribute('title'); // Remove default tooltip
        
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'cyber-tooltip';
            tooltip.textContent = tooltipText;
            tooltip.style.cssText = `
                position: absolute;
                background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
                color: #00ffff;
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid #333;
                font-size: 12px;
                font-family: 'Orbitron', monospace;
                z-index: 1000;
                pointer-events: none;
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
                transform: translateY(-100%);
                margin-top: -10px;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top + window.scrollY + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.cyber-tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}

/**
 * Particle Effects
 */
function initializeParticleEffects() {
    // Create particle system for background
    const particleContainer = document.createElement('div');
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -3;
    `;
    document.body.appendChild(particleContainer);

    // Create particles
    for (let i = 0; i < 50; i++) {
        createParticle(particleContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: absolute;
        width: 2px;
        height: 2px;
        background: #00ffff;
        border-radius: 50%;
        opacity: ${Math.random() * 0.5 + 0.2};
        animation: particleFloat ${Math.random() * 10 + 10}s linear infinite;
    `;
    
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 10 + 's';
    
    container.appendChild(particle);

    // Add particle animation CSS if not exists
    if (!document.querySelector('#particle-style')) {
        const style = document.createElement('style');
        style.id = 'particle-style';
        style.textContent = `
            @keyframes particleFloat {
                0% { 
                    transform: translateY(0) translateX(0) scale(1);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                }
                90% {
                    opacity: 1;
                }
                100% { 
                    transform: translateY(-100vh) translateX(${Math.random() * 200 - 100}px) scale(0);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Cyber Message System
 */
function showCyberMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `cyber-message cyber-message-${type}`;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
        border: 1px solid ${type === 'error' ? '#ff0040' : '#00ffff'};
        border-left: 4px solid ${type === 'error' ? '#ff0040' : '#00ffff'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 500;
        box-shadow: 0 0 20px rgba(${type === 'error' ? '255, 0, 64' : '0, 255, 255'}, 0.3);
        z-index: 9999;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 350px;
    `;
    
    messageDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: white; font-size: 18px; cursor: pointer; margin-left: auto;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(messageDiv);
    
    // Animate in
    setTimeout(() => {
        messageDiv.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        messageDiv.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 5000);
}

/**
 * Search Result Animations
 */
function animateSearchResults() {
    const resultItems = document.querySelectorAll('.platform-card, .info-row');
    
    resultItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        item.style.transition = `opacity 0.4s ease ${index * 0.1}s, transform 0.4s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, index * 100);
    });
}

/**
 * Terminal-style Console Output
 */
function initializeTerminalOutput() {
    // Add terminal-style logging for debugging
    const originalLog = console.log;
    console.log = function(...args) {
        originalLog.apply(console, ['[OSINT-TOOLS]', ...args]);
    };
    
    // Add cyber-themed console styling
    console.log('%c🔮 OSINT Tools Initialized', 'color: #00ffff; font-weight: bold; font-size: 14px;');
    console.log('%c⚡ Cyber Interface Active', 'color: #00ff00; font-weight: bold;');
    console.log('%c🛡️ Security Protocols Enabled', 'color: #ff00ff; font-weight: bold;');
}

/**
 * Keyboard Shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="username"], input[name="domain"], input[name="ip_address"], input[name="query"], input[name="url"]');
            if (searchInput) {
                searchInput.focus();
                showCyberMessage('Search activated - Start typing', 'info');
            }
        }
        
        // Escape to clear all inputs
        if (e.key === 'Escape') {
            const inputs = document.querySelectorAll('input');
            inputs.forEach(input => {
                if (input.type !== 'submit' && input.type !== 'button') {
                    input.value = '';
                }
            });
            document.activeElement.blur();
        }
    });
}

/**
 * Performance Monitoring
 */
function initializePerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`⚡ Page loaded in ${Math.round(loadTime)}ms`);
        
        if (loadTime > 3000) {
            console.warn('⚠️ Slow page load detected');
        }
    });
    
    // Monitor search operations
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const startTime = performance.now();
            console.log('🔍 Search operation started');
            
            // This would normally be handled by server response
            // but we can log client-side timing
            setTimeout(() => {
                const endTime = performance.now();
                console.log(`🔍 Search completed in ${Math.round(endTime - startTime)}ms`);
            }, 1000);
        });
    });
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    initializeTerminalOutput();
    initializeKeyboardShortcuts();
    initializePerformanceMonitoring();
    
    // Animate search results if they exist
    if (document.querySelector('.results-section')) {
        animateSearchResults();
    }
});

// Global utility functions
window.CyberUtils = {
    showMessage: showCyberMessage,
    animateResults: animateSearchResults,
    typeWriter: typeWriterEffect
};

// Add some fun Easter eggs
document.addEventListener('keydown', function(e) {
    // Konami code for special effect
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA'];
    window.konamiSequence = window.konamiSequence || [];
    
    window.konamiSequence.push(e.code);
    if (window.konamiSequence.length > konamiCode.length) {
        window.konamiSequence = window.konamiSequence.slice(-konamiCode.length);
    }
    
    if (JSON.stringify(window.konamiSequence) === JSON.stringify(konamiCode)) {
        // Special cyber effect
        document.body.style.animation = 'cyber-glitch 2s ease-in-out';
        showCyberMessage('🔮 Cyber Mode Activated! Welcome to the Matrix...', 'info');
        
        // Add glitch effect CSS
        if (!document.querySelector('#glitch-style')) {
            const style = document.createElement('style');
            style.id = 'glitch-style';
            style.textContent = `
                @keyframes cyber-glitch {
                    0%, 100% { filter: none; }
                    20% { filter: hue-rotate(90deg) saturate(5); }
                    40% { filter: invert(1) hue-rotate(180deg); }
                    60% { filter: sepia(1) hue-rotate(270deg); }
                    80% { filter: contrast(2) brightness(0.5); }
                }
            `;
            document.head.appendChild(style);
        }
        
        window.konamiSequence = [];
    }
});

console.log('%c🚀 OSINT Tools JavaScript Loaded Successfully!', 'color: #00ffff; font-weight: bold; font-size: 16px;');
