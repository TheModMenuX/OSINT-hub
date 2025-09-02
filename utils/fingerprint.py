"""
Advanced device fingerprinting capabilities
"""

import hashlib
import json
import re
from user_agents import parse
import logging

logger = logging.getLogger(__name__)

class DeviceFingerprinter:
    def __init__(self):
        self.fingerprint_cache = {}
        
    def enhance_data(self, data, request):
        """Enhance collected data with advanced fingerprinting"""
        enhanced = data.copy()
        
        # Basic request information
        ip_address = self._get_real_ip(request)
        user_agent = request.headers.get('User-Agent', '')
        
        # Parse user agent
        ua_info = self._parse_user_agent(user_agent)
        
        # Enhanced device information
        device_info = {
            'ip_address': ip_address,
            'user_agent': user_agent,
            'parsed_ua': ua_info,
            'headers': dict(request.headers),
            'fingerprint_id': self._generate_fingerprint_id(data, request)
        }
        
        # Add client-side fingerprinting data if available
        if 'device' in data:
            device_info.update(data['device'])
            
        enhanced['device'] = device_info
        
        # Enhance location data
        if 'location' in data:
            enhanced['location'] = self._enhance_location_data(data['location'])
            
        # Add risk assessment
        enhanced['risk_assessment'] = self._assess_risk(enhanced)
        
        return enhanced
        
    def _get_real_ip(self, request):
        """Get real IP address considering proxies"""
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
            
        return request.environ.get('REMOTE_ADDR', request.remote_addr)
        
    def _parse_user_agent(self, user_agent):
        """Parse user agent string"""
        try:
            ua = parse(user_agent)
            return {
                'browser': {
                    'family': ua.browser.family,
                    'version': ua.browser.version_string
                },
                'os': {
                    'family': ua.os.family,
                    'version': ua.os.version_string
                },
                'device': {
                    'family': ua.device.family,
                    'brand': ua.device.brand,
                    'model': ua.device.model
                },
                'is_mobile': ua.is_mobile,
                'is_tablet': ua.is_tablet,
                'is_pc': ua.is_pc,
                'is_bot': ua.is_bot
            }
        except Exception as e:
            logger.error(f"Error parsing user agent: {e}")
            return {'error': str(e)}
            
    def _generate_fingerprint_id(self, data, request):
        """Generate unique fingerprint ID"""
        fingerprint_data = {
            'user_agent': request.headers.get('User-Agent', ''),
            'accept_language': request.headers.get('Accept-Language', ''),
            'accept_encoding': request.headers.get('Accept-Encoding', ''),
            'screen_resolution': data.get('device', {}).get('screen_resolution', ''),
            'timezone': data.get('device', {}).get('timezone', ''),
            'canvas_fingerprint': data.get('device', {}).get('canvas_fingerprint', ''),
            'webgl_fingerprint': data.get('device', {}).get('webgl_fingerprint', '')
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
        
    def _enhance_location_data(self, location):
        """Enhance location data with additional context"""
        enhanced_location = location.copy()
        
        # Accuracy classification
        accuracy = location.get('accuracy', float('inf'))
        if accuracy < 10:
            enhanced_location['accuracy_level'] = 'very_high'
        elif accuracy < 50:
            enhanced_location['accuracy_level'] = 'high'
        elif accuracy < 100:
            enhanced_location['accuracy_level'] = 'medium'
        else:
            enhanced_location['accuracy_level'] = 'low'
            
        # Location source estimation
        if accuracy < 20:
            enhanced_location['likely_source'] = 'gps'
        elif accuracy < 100:
            enhanced_location['likely_source'] = 'wifi'
        else:
            enhanced_location['likely_source'] = 'cell_tower'
            
        return enhanced_location
        
    def _assess_risk(self, data):
        """Assess risk level based on various factors"""
        risk_score = 0
        risk_factors = []
        
        # Check for proxy/VPN indicators
        headers = data.get('device', {}).get('headers', {})
        if any(header in headers for header in ['X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP']):
            risk_score += 20
            risk_factors.append('proxy_detected')
            
        # Check for bot indicators
        ua_info = data.get('device', {}).get('parsed_ua', {})
        if ua_info.get('is_bot', False):
            risk_score += 50
            risk_factors.append('bot_detected')
            
        # Check for suspicious user agent
        user_agent = data.get('device', {}).get('user_agent', '')
        if self._is_suspicious_user_agent(user_agent):
            risk_score += 30
            risk_factors.append('suspicious_user_agent')
            
        # Check location accuracy
        accuracy = data.get('location', {}).get('accuracy', float('inf'))
        if accuracy > 1000:
            risk_score += 25
            risk_factors.append('low_location_accuracy')
            
        # Determine risk level
        if risk_score >= 70:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
            
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }
        
    def _is_suspicious_user_agent(self, user_agent):
        """Check if user agent is suspicious"""
        suspicious_patterns = [
            r'curl',
            r'wget',
            r'python',
            r'bot',
            r'crawler',
            r'spider',
            r'scraper'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(re.search(pattern, user_agent_lower) for pattern in suspicious_patterns)
        
    def get_fingerprint_stats(self, db):
        """Get fingerprinting statistics"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Unique fingerprints
                cursor.execute('SELECT COUNT(DISTINCT canvas_fingerprint) as unique_canvas FROM device_fingerprints WHERE canvas_fingerprint IS NOT NULL')
                unique_canvas = cursor.fetchone()['unique_canvas']
                
                # Most common platforms
                cursor.execute('SELECT platform, COUNT(*) as count FROM device_fingerprints WHERE platform IS NOT NULL GROUP BY platform ORDER BY count DESC LIMIT 5')
                common_platforms = dict(cursor.fetchall())
                
                # Most common resolutions
                cursor.execute('SELECT screen_resolution, COUNT(*) as count FROM device_fingerprints WHERE screen_resolution IS NOT NULL GROUP BY screen_resolution ORDER BY count DESC LIMIT 5')
                common_resolutions = dict(cursor.fetchall())
                
                return {
                    'unique_fingerprints': unique_canvas,
                    'common_platforms': common_platforms,
                    'common_resolutions': common_resolutions
                }
        except Exception as e:
            logger.error(f"Error getting fingerprint stats: {e}")
            return {}
