"""
Enhanced tunnel management with multiple service support
"""

import subprocess
import requests
import time
import threading
import os
import signal
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TunnelManager:
    def __init__(self):
        self.active_tunnel = None
        self.tunnel_process = None
        self.tunnel_url = None
        self.tunnel_service = None
        
    def start_tunnel(self, service='ngrok', port=5000, subdomain=None):
        """Start tunnel service"""
        self.stop_tunnel()  # Stop any existing tunnel
        
        if service == 'ngrok':
            return self._start_ngrok(port, subdomain)
        elif service == 'serveo':
            return self._start_serveo(port, subdomain)
        elif service == 'localtunnel':
            return self._start_localtunnel(port, subdomain)
        else:
            raise ValueError(f"Unsupported tunnel service: {service}")
            
    def _start_ngrok(self, port, subdomain=None):
        """Start ngrok tunnel"""
        try:
            # Check if ngrok is installed
            subprocess.check_output(['which', 'ngrok'], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            raise Exception("ngrok is not installed. Please install ngrok first.")
            
        # Prepare command
        cmd = ['ngrok', 'http', str(port), '--log=stdout']
        
        if subdomain:
            cmd.extend(['--subdomain', subdomain])
            
        # Set auth token if available
        auth_token = os.getenv('NGROK_AUTH_TOKEN')
        if auth_token:
            subprocess.run(['ngrok', 'config', 'add-authtoken', auth_token], 
                         capture_output=True)
            
        # Start ngrok
        self.tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait for tunnel to be ready and get URL
        url = self._wait_for_ngrok_url()
        if url:
            self.tunnel_url = url
            self.tunnel_service = 'ngrok'
            self.active_tunnel = True
            logger.info(f"ngrok tunnel started: {url}")
            return url
        else:
            raise Exception("Failed to get ngrok URL")
            
    def _wait_for_ngrok_url(self, timeout=30):
        """Wait for ngrok to be ready and get public URL"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=1)
                if response.status_code == 200:
                    tunnels = response.json()['tunnels']
                    if tunnels:
                        public_url = tunnels[0]['public_url']
                        if public_url.startswith('https://'):
                            return public_url
            except:
                pass
                
            time.sleep(1)
            
        return None
        
    def _start_serveo(self, port, subdomain=None):
        """Start serveo tunnel"""
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-R']
        
        if subdomain:
            cmd.append(f'{subdomain}.serveo.net:{port}:localhost:{port}')
            url = f'https://{subdomain}.serveo.net'
        else:
            cmd.append(f'80:localhost:{port}')
            url = None  # Will be extracted from output
            
        cmd.append('serveo.net')
        
        self.tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Extract URL from output if no subdomain specified
        if not url:
            url = self._wait_for_serveo_url()
            
        if url:
            self.tunnel_url = url
            self.tunnel_service = 'serveo'
            self.active_tunnel = True
            logger.info(f"serveo tunnel started: {url}")
            return url
        else:
            raise Exception("Failed to start serveo tunnel")
            
    def _wait_for_serveo_url(self, timeout=30):
        """Wait for serveo URL from output"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.tunnel_process.poll() is not None:
                break
                
            try:
                line = self.tunnel_process.stdout.readline()
                if 'Forwarding HTTP traffic from' in line:
                    # Extract URL from line
                    url_start = line.find('https://')
                    if url_start != -1:
                        url = line[url_start:].strip()
                        return url
            except:
                pass
                
        return None
        
    def _start_localtunnel(self, port, subdomain=None):
        """Start localtunnel"""
        try:
            # Check if lt is installed
            subprocess.check_output(['which', 'lt'], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            raise Exception("localtunnel is not installed. Please install it with: npm install -g localtunnel")
            
        cmd = ['lt', '--port', str(port)]
        
        if subdomain:
            cmd.extend(['--subdomain', subdomain])
            
        self.tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait for URL
        url = self._wait_for_localtunnel_url()
        if url:
            self.tunnel_url = url
            self.tunnel_service = 'localtunnel'
            self.active_tunnel = True
            logger.info(f"localtunnel started: {url}")
            return url
        else:
            raise Exception("Failed to start localtunnel")
            
    def _wait_for_localtunnel_url(self, timeout=30):
        """Wait for localtunnel URL"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.tunnel_process.poll() is not None:
                break
                
            try:
                line = self.tunnel_process.stdout.readline()
                if 'your url is:' in line:
                    url = line.split('your url is:')[1].strip()
                    return url
            except:
                pass
                
        return None
        
    def stop_tunnel(self):
        """Stop active tunnel"""
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tunnel_process.kill()
            except:
                pass
                
        self.tunnel_process = None
        self.tunnel_url = None
        self.tunnel_service = None
        self.active_tunnel = False
        logger.info("Tunnel stopped")
        
    def get_status(self):
        """Get tunnel status"""
        if self.active_tunnel and self.tunnel_process:
            # Check if process is still running
            if self.tunnel_process.poll() is None:
                return {
                    'active': True,
                    'service': self.tunnel_service,
                    'url': self.tunnel_url,
                    'status': 'running'
                }
            else:
                self.active_tunnel = False
                return {
                    'active': False,
                    'service': None,
                    'url': None,
                    'status': 'stopped'
                }
        else:
            return {
                'active': False,
                'service': None,
                'url': None,
                'status': 'inactive'
            }
            
    def get_url(self):
        """Get current tunnel URL"""
        return self.tunnel_url if self.active_tunnel else None
        
    def restart_tunnel(self):
        """Restart current tunnel"""
        if self.tunnel_service:
            service = self.tunnel_service
            port = 5000  # Default port
            self.stop_tunnel()
            time.sleep(2)
            return self.start_tunnel(service, port)
        else:
            raise Exception("No tunnel service configured")
