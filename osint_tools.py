import requests
import json
import time
import os
import logging
import re
import socket
import dns.resolver
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import whois
from web_scraper import get_website_text_content

class OSINTTools:
    """Comprehensive OSINT toolkit for intelligence gathering"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # API Keys from environment variables
        self.ipgeolocation_api_key = os.getenv('IPGEOLOCATION_API_KEY', '')
        self.hunter_api_key = os.getenv('HUNTER_API_KEY', '')
        self.shodan_api_key = os.getenv('SHODAN_API_KEY', '')
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # seconds
        
    def _rate_limit(self, api_name: str):
        """Simple rate limiting mechanism"""
        current_time = time.time()
        if api_name in self.last_request_time:
            time_diff = current_time - self.last_request_time[api_name]
            if time_diff < self.min_request_interval:
                time.sleep(self.min_request_interval - time_diff)
        self.last_request_time[api_name] = time.time()
    
    def _send_discord_alert(self, message: str):
        """Send alert to Discord webhook"""
        if not self.discord_webhook_url:
            return
        
        try:
            payload = {
                'content': f'🔍 OSINT Alert: {message}',
                'username': 'OSINT Bot'
            }
            self.session.post(self.discord_webhook_url, json=payload)
        except Exception as e:
            logging.error(f"Discord webhook error: {e}")
    
    def ip_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """Get IP geolocation information"""
        self._rate_limit('ip_geolocation')
        
        result = {
            'ip': ip_address,
            'location': {},
            'isp': {},
            'security': {},
            'dns': {},
            'ports': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Validate IP address
            socket.inet_aton(ip_address)
            
            # Basic geolocation (free service)
            try:
                response = self.session.get(f'http://ip-api.com/json/{ip_address}')
                if response.status_code == 200:
                    data = response.json()
                    result['location'] = {
                        'country': data.get('country', 'Unknown'),
                        'country_code': data.get('countryCode', 'Unknown'),
                        'region': data.get('regionName', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'zip_code': data.get('zip', 'Unknown'),
                        'latitude': data.get('lat', 0),
                        'longitude': data.get('lon', 0),
                        'timezone': data.get('timezone', 'Unknown'),
                        'isp': data.get('isp', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'as': data.get('as', 'Unknown')
                    }
            except Exception as e:
                logging.error(f"IP-API error: {e}")
                result['location']['error'] = 'Geolocation service unavailable'
            
            # Enhanced geolocation with IPGeolocation API
            if self.ipgeolocation_api_key:
                try:
                    response = self.session.get(
                        f'https://api.ipgeolocation.io/ipgeo?apiKey={self.ipgeolocation_api_key}&ip={ip_address}'
                    )
                    if response.status_code == 200:
                        data = response.json()
                        result['location'].update({
                            'district': data.get('district', 'Unknown'),
                            'calling_code': data.get('calling_code', 'Unknown'),
                            'currency': data.get('currency', {}).get('name', 'Unknown'),
                            'languages': data.get('languages', 'Unknown')
                        })
                        result['security'] = {
                            'is_eu': data.get('is_eu', False),
                            'threat_level': 'Low'  # Default assumption
                        }
                except Exception as e:
                    logging.error(f"IPGeolocation API error: {e}")
            
            # DNS lookup
            try:
                hostname = socket.gethostbyaddr(ip_address)[0]
                result['dns']['hostname'] = hostname
            except:
                result['dns']['hostname'] = 'No reverse DNS'
            
            # Port scanning (basic)
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
            open_ports = []
            
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    result_port = sock.connect_ex((ip_address, port))
                    if result_port == 0:
                        open_ports.append(port)
                except:
                    pass
                finally:
                    sock.close()
            
            result['ports'] = {
                'open_ports': open_ports,
                'total_scanned': len(common_ports)
            }
            
            # Shodan integration
            if self.shodan_api_key:
                try:
                    response = self.session.get(
                        f'https://api.shodan.io/shodan/host/{ip_address}?key={self.shodan_api_key}'
                    )
                    if response.status_code == 200:
                        shodan_data = response.json()
                        result['shodan'] = {
                            'vulns': list(shodan_data.get('vulns', [])),
                            'ports': shodan_data.get('ports', []),
                            'hostnames': shodan_data.get('hostnames', []),
                            'tags': shodan_data.get('tags', [])
                        }
                except Exception as e:
                    logging.error(f"Shodan API error: {e}")
            
            # Send Discord alert for suspicious IPs
            if result['ports']['open_ports']:
                self._send_discord_alert(f"IP {ip_address} has open ports: {result['ports']['open_ports']}")
                
        except socket.error:
            result['error'] = 'Invalid IP address format'
        except Exception as e:
            logging.error(f"IP geolocation error: {e}")
            result['error'] = str(e)
        
        return result
    
    def email_search(self, email: str) -> Dict[str, Any]:
        """Search for email information and breaches"""
        self._rate_limit('email_search')
        
        result = {
            'email': email,
            'validation': {},
            'breaches': {},
            'social_media': {},
            'domain_info': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Email validation
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid = re.match(email_regex, email) is not None
            
            result['validation'] = {
                'is_valid': is_valid,
                'format_check': is_valid
            }
            
            if not is_valid:
                result['error'] = 'Invalid email format'
                return result
            
            # Extract domain
            domain = email.split('@')[1]
            result['domain_info']['domain'] = domain
            
            # Hunter.io API for email verification
            if self.hunter_api_key:
                try:
                    response = self.session.get(
                        f'https://api.hunter.io/v2/email-verifier?email={email}&api_key={self.hunter_api_key}'
                    )
                    if response.status_code == 200:
                        hunter_data = response.json().get('data', {})
                        result['validation'].update({
                            'deliverable': hunter_data.get('result', 'unknown'),
                            'mx_records': hunter_data.get('mx_records', False),
                            'smtp_server': hunter_data.get('smtp_server', False),
                            'smtp_check': hunter_data.get('smtp_check', False)
                        })
                except Exception as e:
                    logging.error(f"Hunter.io API error: {e}")
            
            # Domain analysis
            try:
                mx_records = []
                try:
                    mx_results = dns.resolver.resolve(domain, 'MX')
                    mx_records = [str(mx) for mx in mx_results]
                except:
                    pass
                
                result['domain_info'].update({
                    'mx_records': mx_records,
                    'has_mx': len(mx_records) > 0
                })
            except Exception as e:
                logging.error(f"DNS lookup error: {e}")
            
            # Social media presence check (basic)
            social_platforms = {
                'gravatar': f'https://gravatar.com/{email}',
                'skype': f'skype:{email.split("@")[0]}'
            }
            
            result['social_media'] = {
                'potential_profiles': social_platforms,
                'checked_platforms': list(social_platforms.keys())
            }
            
            # Send Discord alert
            self._send_discord_alert(f"Email search performed for: {email}")
            
        except Exception as e:
            logging.error(f"Email search error: {e}")
            result['error'] = str(e)
        
        return result
    
    def domain_analysis(self, domain: str) -> Dict[str, Any]:
        """Comprehensive domain analysis"""
        self._rate_limit('domain_analysis')
        
        result = {
            'domain': domain,
            'whois': {},
            'dns': {},
            'subdomains': {},
            'security': {},
            'content': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Clean domain
            domain = domain.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
            
            # WHOIS lookup
            try:
                w = whois.whois(domain)
                result['whois'] = {
                    'registrar': w.registrar,
                    'creation_date': str(w.creation_date) if w.creation_date else 'Unknown',
                    'expiration_date': str(w.expiration_date) if w.expiration_date else 'Unknown',
                    'name_servers': w.name_servers if w.name_servers else [],
                    'status': w.status if w.status else 'Unknown',
                    'emails': w.emails if w.emails else [],
                    'country': w.country if hasattr(w, 'country') else 'Unknown'
                }
            except Exception as e:
                logging.error(f"WHOIS error: {e}")
                result['whois']['error'] = 'WHOIS lookup failed'
            
            # DNS records
            dns_records = {}
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
            
            for record_type in record_types:
                try:
                    records = dns.resolver.resolve(domain, record_type)
                    dns_records[record_type] = [str(record) for record in records]
                except:
                    dns_records[record_type] = []
            
            result['dns'] = dns_records
            
            # IP address resolution
            try:
                ip_address = socket.gethostbyname(domain)
                result['dns']['ip_address'] = ip_address
            except:
                result['dns']['ip_address'] = 'Unknown'
            
            # Common subdomain check
            common_subdomains = ['www', 'mail', 'ftp', 'admin', 'api', 'blog', 'shop', 'dev', 'test']
            found_subdomains = []
            
            for subdomain in common_subdomains:
                try:
                    full_domain = f"{subdomain}.{domain}"
                    socket.gethostbyname(full_domain)
                    found_subdomains.append(full_domain)
                except:
                    pass
            
            result['subdomains'] = {
                'found': found_subdomains,
                'total_checked': len(common_subdomains)
            }
            
            # Security checks
            security_info = {
                'has_www': 'www' in found_subdomains,
                'has_mail': any('mail' in sub for sub in found_subdomains),
                'mx_configured': len(dns_records.get('MX', [])) > 0,
                'name_servers_count': len(dns_records.get('NS', []))
            }
            
            result['security'] = security_info
            
            # Content analysis using web scraper
            try:
                content = get_website_text_content(f"https://{domain}")
                if content:
                    result['content'] = {
                        'content_length': len(content),
                        'has_content': True,
                        'preview': content[:500] + '...' if len(content) > 500 else content
                    }
                else:
                    result['content'] = {
                        'has_content': False,
                        'error': 'Could not extract content'
                    }
            except Exception as e:
                logging.error(f"Content analysis error: {e}")
                result['content'] = {
                    'has_content': False,
                    'error': str(e)
                }
            
            # Send Discord alert
            self._send_discord_alert(f"Domain analysis completed for: {domain}")
            
        except Exception as e:
            logging.error(f"Domain analysis error: {e}")
            result['error'] = str(e)
        
        return result
    
    def username_search(self, username: str) -> Dict[str, Any]:
        """Search username across multiple platforms"""
        self._rate_limit('username_search')
        
        result = {
            'username': username,
            'platforms': {},
            'statistics': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Social media platforms to check
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}',
            'YouTube': f'https://youtube.com/user/{username}',
            'Pinterest': f'https://pinterest.com/{username}',
            'TikTok': f'https://tiktok.com/@{username}',
            'Telegram': f'https://t.me/{username}',
            'Medium': f'https://medium.com/@{username}',
            'Dribbble': f'https://dribbble.com/{username}',
            'Behance': f'https://behance.net/{username}',
            'DeviantArt': f'https://deviantart.com/{username}',
            'Steam': f'https://steamcommunity.com/id/{username}',
            'Twitch': f'https://twitch.tv/{username}'
        }
        
        found_platforms = {}
        total_checked = 0
        total_found = 0
        
        try:
            for platform, url in platforms.items():
                total_checked += 1
                try:
                    response = self.session.head(url, timeout=5, allow_redirects=True)
                    
                    # Different platforms have different response patterns
                    if platform == 'GitHub':
                        exists = response.status_code == 200
                    elif platform in ['Twitter', 'Instagram']:
                        exists = response.status_code != 404
                    else:
                        exists = response.status_code in [200, 301, 302]
                    
                    found_platforms[platform] = {
                        'url': url,
                        'exists': exists,
                        'status_code': response.status_code,
                        'last_checked': datetime.now().isoformat()
                    }
                    
                    if exists:
                        total_found += 1
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    found_platforms[platform] = {
                        'url': url,
                        'exists': False,
                        'error': str(e),
                        'last_checked': datetime.now().isoformat()
                    }
            
            result['platforms'] = found_platforms
            result['statistics'] = {
                'total_platforms_checked': total_checked,
                'profiles_found': total_found,
                'success_rate': f"{(total_found/total_checked)*100:.1f}%" if total_checked > 0 else "0%"
            }
            
            # Send Discord alert for significant findings
            if total_found > 5:
                self._send_discord_alert(f"Username '{username}' found on {total_found} platforms")
            
        except Exception as e:
            logging.error(f"Username search error: {e}")
            result['error'] = str(e)
        
        return result
    
    def phone_lookup(self, phone: str) -> Dict[str, Any]:
        """Phone number lookup and analysis"""
        self._rate_limit('phone_lookup')
        
        result = {
            'phone': phone,
            'format': {},
            'location': {},
            'carrier': {},
            'type': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Clean phone number
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            
            result['format'] = {
                'original': phone,
                'cleaned': cleaned_phone,
                'length': len(cleaned_phone)
            }
            
            # Basic validation
            if len(cleaned_phone) < 10:
                result['error'] = 'Phone number too short'
                return result
            
            # Extract country and area codes (basic)
            area_code = None
            if cleaned_phone.startswith('+1') or (len(cleaned_phone) == 10):
                # US/Canada number
                if cleaned_phone.startswith('+1'):
                    area_code = cleaned_phone[2:5]
                    number = cleaned_phone[5:]
                else:
                    area_code = cleaned_phone[:3]
                    number = cleaned_phone[3:]
                
                result['location'] = {
                    'country': 'US/Canada',
                    'area_code': area_code,
                    'number': number,
                    'formatted': f"+1-{area_code}-{number[:3]}-{number[3:]}"
                }
                
                # Area code location mapping (sample)
                area_code_locations = {
                    '212': 'New York, NY',
                    '213': 'Los Angeles, CA',
                    '415': 'San Francisco, CA',
                    '312': 'Chicago, IL',
                    '713': 'Houston, TX',
                    '305': 'Miami, FL',
                    '202': 'Washington, DC',
                    '617': 'Boston, MA'
                }
                
                result['location']['city'] = area_code_locations.get(area_code, 'Unknown')
            
            elif cleaned_phone.startswith('+44'):
                # UK number
                result['location'] = {
                    'country': 'United Kingdom',
                    'formatted': cleaned_phone
                }
            else:
                result['location'] = {
                    'country': 'Unknown',
                    'formatted': cleaned_phone
                }
            
            # Phone type detection (basic heuristics)
            if (len(cleaned_phone) == 10 or cleaned_phone.startswith('+1')) and area_code:
                result['type'] = {
                    'likely_mobile': area_code in ['310', '323', '424', '661', '747', '818'],  # Sample mobile prefixes
                    'likely_landline': area_code in ['212', '213', '415', '312'],  # Sample landline prefixes
                    'confidence': 'low'  # Without proper API, confidence is low
                }
            
            # Carrier information (would need specialized API)
            result['carrier'] = {
                'name': 'Unknown - Requires specialized API',
                'type': 'Unknown'
            }
            
            # Send Discord alert
            self._send_discord_alert(f"Phone lookup performed for: {phone}")
            
        except Exception as e:
            logging.error(f"Phone lookup error: {e}")
            result['error'] = str(e)
        
        return result
