import requests
import json
import re
from urllib.parse import urlparse
from services.web_scraper import get_website_text_content

class OSINTTools:
    """Collection of OSINT tools for username, domain, and email searches"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_username(self, username):
        """Search for username across various platforms"""
        results = {
            'username': username,
            'platforms': {},
            'summary': {}
        }
        
        # List of platforms to check
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}',
            'YouTube': f'https://youtube.com/@{username}',
            'TikTok': f'https://tiktok.com/@{username}',
            'Twitch': f'https://twitch.tv/{username}',
            'Steam': f'https://steamcommunity.com/id/{username}',
            'Pinterest': f'https://pinterest.com/{username}'
        }
        
        found_count = 0
        total_checked = 0
        
        for platform, url in platforms.items():
            try:
                response = self.session.get(url, timeout=10, allow_redirects=True)
                total_checked += 1
                
                # Check if profile exists based on response
                if response.status_code == 200:
                    # Additional checks to avoid false positives
                    if self._verify_profile_exists(platform, response.text, username):
                        results['platforms'][platform] = {
                            'url': url,
                            'status': 'found',
                            'response_code': response.status_code
                        }
                        found_count += 1
                    else:
                        results['platforms'][platform] = {
                            'url': url,
                            'status': 'not_found',
                            'response_code': response.status_code
                        }
                else:
                    results['platforms'][platform] = {
                        'url': url,
                        'status': 'not_found',
                        'response_code': response.status_code
                    }
            except requests.RequestException as e:
                results['platforms'][platform] = {
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                }
        
        results['summary'] = {
            'found': found_count,
            'total_checked': total_checked,
            'success_rate': f'{(found_count/total_checked*100):.1f}%' if total_checked > 0 else '0%'
        }
        
        return results
    
    def search_domain(self, domain):
        """Search for domain information"""
        results = {
            'domain': domain,
            'basic_info': {},
            'web_content': {},
            'security_info': {},
            'summary': {}
        }
        
        try:
            # Basic domain validation
            if not self._is_valid_domain(domain):
                results['summary']['error'] = 'Invalid domain format'
                return results
            
            # Get website content
            try:
                url = f'http://{domain}' if not domain.startswith('http') else domain
                content = get_website_text_content(url)
                results['web_content'] = {
                    'url': url,
                    'content_preview': content[:500] + '...' if len(content) > 500 else content,
                    'content_length': len(content),
                    'status': 'success'
                }
            except Exception as e:
                results['web_content'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Basic HTTP check
            try:
                response = self.session.get(f'http://{domain}', timeout=10)
                results['basic_info']['http'] = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'redirects': len(response.history) > 0
                }
            except requests.RequestException as e:
                results['basic_info']['http'] = {
                    'error': str(e)
                }
            
            # HTTPS check
            try:
                response = self.session.get(f'https://{domain}', timeout=10)
                results['basic_info']['https'] = {
                    'status_code': response.status_code,
                    'ssl_available': True
                }
            except requests.RequestException:
                results['basic_info']['https'] = {
                    'ssl_available': False
                }
            
            results['summary']['status'] = 'completed'
            
        except Exception as e:
            results['summary']['error'] = str(e)
        
        return results
    
    def search_email(self, email):
        """Search for email information"""
        results = {
            'email': email,
            'validation': {},
            'domain_info': {},
            'breach_check': {},
            'summary': {}
        }
        
        try:
            # Basic email validation
            if not self._is_valid_email(email):
                results['summary']['error'] = 'Invalid email format'
                return results
            
            # Extract domain from email
            domain = email.split('@')[1]
            
            # Email format validation
            results['validation'] = {
                'format_valid': self._is_valid_email(email),
                'domain': domain,
                'local_part': email.split('@')[0]
            }
            
            # Check domain of email
            domain_results = self.search_domain(domain)
            results['domain_info'] = domain_results
            
            # Note: For security reasons, we don't implement actual breach checking
            # In a real implementation, you would integrate with services like HaveIBeenPwned API
            results['breach_check'] = {
                'note': 'Breach checking requires external API integration',
                'recommendation': 'Use services like HaveIBeenPwned for breach verification'
            }
            
            results['summary']['status'] = 'completed'
            
        except Exception as e:
            results['summary']['error'] = str(e)
        
        return results
    
    def _verify_profile_exists(self, platform, html_content, username):
        """Verify if a profile actually exists by checking page content"""
        html_lower = html_content.lower()
        username_lower = username.lower()
        
        # Platform-specific verification logic
        if platform == 'GitHub':
            return 'not found' not in html_lower and '404' not in html_lower
        elif platform == 'Twitter':
            return 'this account doesn\'t exist' not in html_lower
        elif platform == 'Instagram':
            return 'page not found' not in html_lower and 'sorry' not in html_lower
        elif platform == 'Reddit':
            return 'page not found' not in html_lower and 'user not found' not in html_lower
        else:
            # Generic check - look for common 404 indicators
            error_indicators = ['404', 'not found', 'page not found', 'user not found', 'profile not found']
            return not any(indicator in html_lower for indicator in error_indicators)
    
    def _is_valid_domain(self, domain):
        """Basic domain validation"""
        pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(pattern.match(domain)) and len(domain) <= 253
    
    def _is_valid_email(self, email):
        """Basic email validation"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))
