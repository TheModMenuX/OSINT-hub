/**
 * Enhanced Device Fingerprinting Library
 * Collects comprehensive device and browser information
 */

class DeviceFingerprinter {
    constructor() {
        this.fingerprint = {};
        this.canvasFingerprint = null;
        this.webglFingerprint = null;
        this.audioFingerprint = null;
    }
    
    async collectFingerprint() {
        this.fingerprint = {
            // Basic browser information
            userAgent: navigator.userAgent,
            language: navigator.language,
            languages: navigator.languages,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            doNotTrack: navigator.doNotTrack,
            
            // Screen information
            screen: {
                width: screen.width,
                height: screen.height,
                availWidth: screen.availWidth,
                availHeight: screen.availHeight,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth
            },
            
            // Window information
            window: {
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                outerWidth: window.outerWidth,
                outerHeight: window.outerHeight,
                devicePixelRatio: window.devicePixelRatio
            },
            
            // Timezone information
            timezone: {
                offset: new Date().getTimezoneOffset(),
                zone: Intl.DateTimeFormat().resolvedOptions().timeZone
            },
            
            // Hardware information
            hardware: {
                cores: navigator.hardwareConcurrency,
                memory: navigator.deviceMemory,
                connection: this.getConnectionInfo()
            },
            
            // Plugins and features
            plugins: this.getPlugins(),
            features: this.getFeatures(),
            
            // Advanced fingerprints
            canvas: await this.getCanvasFingerprint(),
            webgl: await this.getWebGLFingerprint(),
            audio: await this.getAudioFingerprint(),
            fonts: await this.getFontFingerprint(),
            
            // Browser capabilities
            capabilities: this.getBrowserCapabilities(),
            
            // Permissions
            permissions: await this.getPermissions(),
            
            // Timestamp
            timestamp: Date.now()
        };
        
        return this.fingerprint;
    }
    
    getConnectionInfo() {
        if (navigator.connection) {
            return {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt,
                saveData: navigator.connection.saveData
            };
        }
        return null;
    }
    
    getPlugins() {
        const plugins = [];
        for (let i = 0; i < navigator.plugins.length; i++) {
            const plugin = navigator.plugins[i];
            plugins.push({
                name: plugin.name,
                description: plugin.description,
                filename: plugin.filename,
                version: plugin.version
            });
        }
        return plugins;
    }
    
    getFeatures() {
        return {
            webgl: !!window.WebGLRenderingContext,
            webgl2: !!window.WebGL2RenderingContext,
            webrtc: !!(navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia),
            canvas: !!document.createElement('canvas').getContext,
            localStorage: !!window.localStorage,
            sessionStorage: !!window.sessionStorage,
            indexedDB: !!window.indexedDB,
            webWorkers: !!window.Worker,
            serviceWorkers: !!navigator.serviceWorker,
            geolocation: !!navigator.geolocation,
            accelerometer: !!window.DeviceMotionEvent,
            gyroscope: !!window.DeviceOrientationEvent,
            touchSupport: 'ontouchstart' in window,
            pointerEvents: !!window.PointerEvent,
            webAssembly: !!window.WebAssembly,
            speechRecognition: !!(window.SpeechRecognition || window.webkitSpeechRecognition),
            notifications: !!window.Notification,
            vibration: !!navigator.vibrate,
            battery: !!navigator.getBattery,
            credentials: !!navigator.credentials,
            mediaDevices: !!navigator.mediaDevices,
            bluetooth: !!navigator.bluetooth,
            usb: !!navigator.usb
        };
    }
    
    async getCanvasFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = 200;
            canvas.height = 50;
            
            // Draw text with various styles
            ctx.textBaseline = 'top';
            ctx.font = '14px "Arial"';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('Enhanced Seeker 🔍', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.fillText('Device Fingerprint', 4, 30);
            
            // Draw some shapes
            ctx.globalCompositeOperation = 'multiply';
            ctx.fillStyle = 'rgb(255,0,255)';
            ctx.beginPath();
            ctx.arc(50, 25, 20, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.fill();
            
            ctx.fillStyle = 'rgb(0,255,255)';
            ctx.beginPath();
            ctx.arc(100, 25, 20, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.fill();
            
            return canvas.toDataURL();
        } catch (error) {
            console.error('Canvas fingerprint error:', error);
            return null;
        }
    }
    
    async getWebGLFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            
            if (!gl) return null;
            
            const fingerprint = {
                vendor: gl.getParameter(gl.VENDOR),
                renderer: gl.getParameter(gl.RENDERER),
                version: gl.getParameter(gl.VERSION),
                shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
                extensions: gl.getSupportedExtensions(),
                maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
                maxViewportDims: gl.getParameter(gl.MAX_VIEWPORT_DIMS),
                maxVertexAttribs: gl.getParameter(gl.MAX_VERTEX_ATTRIBS),
                maxVertexUniformVectors: gl.getParameter(gl.MAX_VERTEX_UNIFORM_VECTORS),
                maxFragmentUniformVectors: gl.getParameter(gl.MAX_FRAGMENT_UNIFORM_VECTORS),
                maxVaryingVectors: gl.getParameter(gl.MAX_VARYING_VECTORS)
            };
            
            // Additional WebGL debugging info
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                fingerprint.unmaskedVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                fingerprint.unmaskedRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            }
            
            return fingerprint;
        } catch (error) {
            console.error('WebGL fingerprint error:', error);
            return null;
        }
    }
    
    async getAudioFingerprint() {
        try {
            if (!window.AudioContext && !window.webkitAudioContext) {
                return null;
            }
            
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const analyser = audioContext.createAnalyser();
            const gainNode = audioContext.createGain();
            const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
            
            oscillator.type = 'triangle';
            oscillator.frequency.setValueAtTime(10000, audioContext.currentTime);
            
            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            
            oscillator.connect(analyser);
            analyser.connect(scriptProcessor);
            scriptProcessor.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.start(0);
            
            return new Promise((resolve) => {
                let sample = 0;
                const fingerprint = [];
                
                scriptProcessor.onaudioprocess = function(bins) {
                    if (sample++ > 4) {
                        const output = bins.outputBuffer.getChannelData(0);
                        for (let i = 0; i < output.length; i++) {
                            fingerprint.push(output[i]);
                        }
                        
                        oscillator.stop();
                        scriptProcessor.disconnect();
                        audioContext.close();
                        
                        // Create hash from audio data
                        const hash = fingerprint.slice(0, 100).join('');
                        resolve(hash);
                        return;
                    }
                };
                
                // Fallback timeout
                setTimeout(() => {
                    resolve(null);
                }, 1000);
            });
        } catch (error) {
            console.error('Audio fingerprint error:', error);
            return null;
        }
    }
    
    async getFontFingerprint() {
        const fonts = [
            'Arial', 'Arial Black', 'Arial Narrow', 'Arial Unicode MS',
            'Calibri', 'Cambria', 'Courier', 'Courier New', 'Georgia',
            'Helvetica', 'Impact', 'Lucida Console', 'Lucida Sans Unicode',
            'Microsoft Sans Serif', 'Palatino', 'Tahoma', 'Times',
            'Times New Roman', 'Trebuchet MS', 'Verdana', 'Comic Sans MS',
            'Consolas', 'Monaco', 'Menlo', 'Source Code Pro'
        ];
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const testString = 'Enhanced Seeker Font Test 123!@#';
        const baselines = {};
        
        // Get baseline measurements
        ctx.font = '72px monospace';
        for (const font of fonts) {
            ctx.font = `72px ${font}, monospace`;
            baselines[font] = ctx.measureText(testString).width;
        }
        
        return baselines;
    }
    
    getBrowserCapabilities() {
        return {
            // CSS capabilities
            css: {
                flexbox: CSS.supports('display', 'flex'),
                grid: CSS.supports('display', 'grid'),
                customProperties: CSS.supports('--test', 'red'),
                clipPath: CSS.supports('clip-path', 'circle()'),
                filter: CSS.supports('filter', 'blur(1px)'),
                backdropFilter: CSS.supports('backdrop-filter', 'blur(1px)')
            },
            
            // JavaScript capabilities
            javascript: {
                es6Classes: typeof class {} === 'function',
                es6Modules: typeof Symbol !== 'undefined',
                asyncAwait: (async () => {}).constructor === (async function(){}).constructor,
                promises: typeof Promise !== 'undefined',
                symbols: typeof Symbol !== 'undefined',
                proxy: typeof Proxy !== 'undefined',
                weakMap: typeof WeakMap !== 'undefined',
                webAssembly: typeof WebAssembly !== 'undefined'
            },
            
            // DOM capabilities
            dom: {
                shadowDOM: !!HTMLElement.prototype.attachShadow,
                customElements: !!window.customElements,
                intersectionObserver: !!window.IntersectionObserver,
                mutationObserver: !!window.MutationObserver,
                resizeObserver: !!window.ResizeObserver,
                performanceObserver: !!window.PerformanceObserver
            }
        };
    }
    
    async getPermissions() {
        const permissions = {};
        
        if (navigator.permissions) {
            const permissionNames = [
                'geolocation', 'notifications', 'camera', 'microphone',
                'clipboard-read', 'clipboard-write', 'accelerometer',
                'gyroscope', 'magnetometer', 'persistent-storage'
            ];
            
            for (const permission of permissionNames) {
                try {
                    const result = await navigator.permissions.query({ name: permission });
                    permissions[permission] = result.state;
                } catch (error) {
                    permissions[permission] = 'unknown';
                }
            }
        }
        
        return permissions;
    }
    
    generateHash(data) {
        // Simple hash function for fingerprint data
        let hash = 0;
        const str = JSON.stringify(data);
        
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        
        return Math.abs(hash).toString(36);
    }
    
    async getEnhancedFingerprint() {
        const fingerprint = await this.collectFingerprint();
        
        // Generate unique fingerprint hash
        fingerprint.hash = this.generateHash(fingerprint);
        
        // Add confidence score based on available data
        fingerprint.confidence = this.calculateConfidence(fingerprint);
        
        return fingerprint;
    }
    
    calculateConfidence(fingerprint) {
        let score = 0;
        let maxScore = 0;
        
        // Canvas fingerprint
        maxScore += 20;
        if (fingerprint.canvas) score += 20;
        
        // WebGL fingerprint
        maxScore += 15;
        if (fingerprint.webgl) score += 15;
        
        // Audio fingerprint
        maxScore += 15;
        if (fingerprint.audio) score += 15;
        
        // Font fingerprint
        maxScore += 10;
        if (fingerprint.fonts && Object.keys(fingerprint.fonts).length > 10) score += 10;
        
        // Screen resolution
        maxScore += 10;
        if (fingerprint.screen.width && fingerprint.screen.height) score += 10;
        
        // Plugins
        maxScore += 10;
        if (fingerprint.plugins.length > 0) score += 10;
        
        // Hardware info
        maxScore += 10;
        if (fingerprint.hardware.cores) score += 5;
        if (fingerprint.hardware.memory) score += 5;
        
        // Timezone
        maxScore += 5;
        if (fingerprint.timezone.zone) score += 5;
        
        // Languages
        maxScore += 5;
        if (fingerprint.languages && fingerprint.languages.length > 0) score += 5;
        
        return Math.round((score / maxScore) * 100);
    }
}

// Global function for collecting device fingerprint
window.collectDeviceFingerprint = async function() {
    try {
        const fingerprinter = new DeviceFingerprinter();
        const fingerprint = await fingerprinter.getEnhancedFingerprint();
        
        // Add additional runtime information
        fingerprint.screen_resolution = `${fingerprint.screen.width}x${fingerprint.screen.height}`;
        fingerprint.canvas_fingerprint = fingerprint.canvas;
        fingerprint.webgl_fingerprint = JSON.stringify(fingerprint.webgl);
        fingerprint.audio_fingerprint = fingerprint.audio;
        fingerprint.timezone = fingerprint.timezone.zone;
        fingerprint.language = fingerprint.language;
        fingerprint.platform = fingerprint.platform;
        fingerprint.plugins = fingerprint.plugins.map(p => p.name);
        fingerprint.fonts = Object.keys(fingerprint.fonts || {});
        
        return fingerprint;
    } catch (error) {
        console.error('Error collecting device fingerprint:', error);
        
        // Return basic fallback fingerprint
        return {
            userAgent: navigator.userAgent || '',
            language: navigator.language || '',
            platform: navigator.platform || '',
            screen_resolution: screen.width && screen.height ? `${screen.width}x${screen.height}` : '',
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
            timestamp: Date.now(),
            error: error.message
        };
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeviceFingerprinter;
}
