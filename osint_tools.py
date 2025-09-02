import requests
import socket
import json
import re
from urllib.parse import urlparse
from datetime import datetime
import logging

class OSINTTools:
    """Collection of OSINT tools and utilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_username(self, username):
        """Search for username across multiple platforms"""
        results = {
            'username': username,
            'platforms': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}',
            'YouTube': f'https://youtube.com/@{username}',
            'TikTok': f'https://tiktok.com/@{username}',
            'Pinterest': f'https://pinterest.com/{username}',
            'Twitch': f'https://twitch.tv/{username}',
            'Steam': f'https://steamcommunity.com/id/{username}'
        }
        
        for platform, url in platforms.items():
            try:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                results['platforms'][platform] = {
                    'url': url,
                    'status': 'Found' if response.status_code == 200 else 'Not Found',
                    'status_code': response.status_code
                }
            except requests.RequestException as e:
                results['platforms'][platform] = {
                    'url': url,
                    'status': 'Error',
                    'error': str(e)
                }
                logging.error(f"Error checking {platform} for {username}: {str(e)}")
        
        return results
    
    def analyze_domain(self, domain):
        """Analyze domain for OSINT information"""
        results = {
            'domain': domain,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Clean domain name
            if domain.startswith(('http://', 'https://')):
                domain = urlparse(domain).netloc
            
            # DNS Resolution
            try:
                ip_address = socket.gethostbyname(domain)
                results['ip_address'] = ip_address
            except socket.gaierror:
                results['ip_address'] = 'Unable to resolve'
            
            # WHOIS-like information (basic)
            results['whois'] = self._get_domain_info(domain)
            
            # Check if domain is alive
            try:
                response = self.session.head(f'http://{domain}', timeout=10)
                results['http_status'] = response.status_code
                results['server'] = response.headers.get('Server', 'Unknown')
            except requests.RequestException:
                try:
                    response = self.session.head(f'https://{domain}', timeout=10)
                    results['http_status'] = response.status_code
                    results['server'] = response.headers.get('Server', 'Unknown')
                    results['ssl'] = True
                except requests.RequestException:
                    results['http_status'] = 'Unreachable'
            
            # Subdomain enumeration (basic)
            results['subdomains'] = self._find_subdomains(domain)
            
        except Exception as e:
            results['error'] = str(e)
            logging.error(f"Domain analysis error for {domain}: {str(e)}")
        
        return results
    
    def investigate_ip(self, ip_address):
        """Investigate IP address for geolocation and other info"""
        results = {
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Basic IP validation
            socket.inet_aton(ip_address)
            
            # Reverse DNS lookup
            try:
                hostname = socket.gethostbyaddr(ip_address)[0]
                results['hostname'] = hostname
            except socket.herror:
                results['hostname'] = 'No reverse DNS'
            
            # Geolocation (using a free service)
            try:
                geo_response = self.session.get(f'http://ip-api.com/json/{ip_address}', timeout=10)
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    results['geolocation'] = {
                        'country': geo_data.get('country', 'Unknown'),
                        'region': geo_data.get('regionName', 'Unknown'),
                        'city': geo_data.get('city', 'Unknown'),
                        'isp': geo_data.get('isp', 'Unknown'),
                        'org': geo_data.get('org', 'Unknown'),
                        'timezone': geo_data.get('timezone', 'Unknown')
                    }
            except requests.RequestException as e:
                results['geolocation'] = {'error': str(e)}
            
            # Port scanning (common ports only)
            results['open_ports'] = self._scan_common_ports(ip_address)
            
        except socket.error:
            results['error'] = 'Invalid IP address'
        except Exception as e:
            results['error'] = str(e)
            logging.error(f"IP investigation error for {ip_address}: {str(e)}")
        
        return results
    
    def lookup_email(self, email):
        """Email lookup and validation"""
        results = {
            'email': email,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Email format validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            results['valid_format'] = bool(re.match(email_pattern, email))
            
            if not results['valid_format']:
                results['error'] = 'Invalid email format'
                return results
            
            # Extract domain
            domain = email.split('@')[1]
            results['domain'] = domain
            
            # Check if domain exists
            try:
                socket.gethostbyname(domain)
                results['domain_exists'] = True
            except socket.gaierror:
                results['domain_exists'] = False
            
            # Check for disposable email domains
            disposable_domains = [
                '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
                'temp-mail.org', 'throwaway.email'
            ]
            results['is_disposable'] = domain.lower() in disposable_domains
            
            # Social media presence check
            results['social_presence'] = self._check_email_social_presence(email)
            
        except Exception as e:
            results['error'] = str(e)
            logging.error(f"Email lookup error for {email}: {str(e)}")
        
        return results
    
    def lookup_phone(self, phone):
        """Phone number lookup and validation"""
        results = {
            'phone': phone,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Clean phone number
            clean_phone = re.sub(r'[^\d]', '', phone)
            results['clean_phone'] = clean_phone
            
            # Basic validation
            if len(clean_phone) < 10:
                results['valid'] = False
                results['error'] = 'Phone number too short'
                return results
            
            results['valid'] = True
            
            # Country code detection (basic)
            if clean_phone.startswith('1') and len(clean_phone) == 11:
                results['country'] = 'US/Canada'
                results['formatted'] = f"+1 ({clean_phone[1:4]}) {clean_phone[4:7]}-{clean_phone[7:]}"
            elif len(clean_phone) == 10:
                results['country'] = 'US (assumed)'
                results['formatted'] = f"({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}"
            else:
                results['country'] = 'International'
                results['formatted'] = f"+{clean_phone}"
            
            # Carrier lookup would require paid API
            results['carrier'] = 'Not available (requires paid API)'
            
        except Exception as e:
            results['error'] = str(e)
            logging.error(f"Phone lookup error for {phone}: {str(e)}")
        
        return results
    
    def _get_domain_info(self, domain):
        """Get basic domain information"""
        try:
            # This would typically use a WHOIS API, but for demo purposes
            # we'll return basic information
            return {
                'status': 'Active',
                'note': 'Full WHOIS data requires API key'
            }
        except Exception:
            return {'error': 'Unable to retrieve WHOIS data'}
    
    def _find_subdomains(self, domain):
        """Find common subdomains"""
        subdomains = ['www', 'mail', 'ftp', 'admin', 'api', 'blog', 'shop', 'test']
        found = []
        
        for sub in subdomains:
            try:
                full_domain = f"{sub}.{domain}"
                socket.gethostbyname(full_domain)
                found.append(full_domain)
            except socket.gaierror:
                continue
            
            # Limit to prevent long execution
            if len(found) >= 5:
                break
        
        return found
    
    def _scan_common_ports(self, ip_address):
        """Scan common ports"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip_address, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                continue
            
            # Limit scan time
            if len(open_ports) >= 5:
                break
        
        return open_ports
    
    def _check_email_social_presence(self, email):
        """Check for social media presence (basic)"""
        # This would typically involve checking various platforms
        # For demo purposes, return placeholder data
        return {
            'note': 'Social media presence check requires specific API access'
        }
