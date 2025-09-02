"""
Advanced analytics and reporting engine
"""

import json
import csv
import io
from datetime import datetime, timedelta
from collections import defaultdict
import xml.etree.ElementTree as ET
from flask import Response
import logging

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self, db):
        self.db = db
        
    def get_statistics(self):
        """Get comprehensive statistics"""
        base_stats = self.db.get_session_stats()
        
        # Add time-based analytics
        time_stats = self._get_time_statistics()
        location_stats = self._get_location_statistics()
        device_stats = self._get_device_statistics()
        
        return {
            **base_stats,
            'time_analytics': time_stats,
            'location_analytics': location_stats,
            'device_analytics': device_stats,
            'generated_at': datetime.now().isoformat()
        }
        
    def _get_time_statistics(self):
        """Get time-based analytics"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Sessions by hour
                cursor.execute('''
                    SELECT strftime('%H', created_at) as hour, COUNT(*) as count
                    FROM sessions 
                    WHERE created_at >= datetime('now', '-7 days')
                    GROUP BY hour
                    ORDER BY hour
                ''')
                hourly_stats = dict(cursor.fetchall())
                
                # Sessions by day of week
                cursor.execute('''
                    SELECT strftime('%w', created_at) as dow, COUNT(*) as count
                    FROM sessions 
                    WHERE created_at >= datetime('now', '-30 days')
                    GROUP BY dow
                    ORDER BY dow
                ''')
                daily_stats = dict(cursor.fetchall())
                
                # Daily trend (last 30 days)
                cursor.execute('''
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM sessions 
                    WHERE created_at >= datetime('now', '-30 days')
                    GROUP BY date
                    ORDER BY date
                ''')
                daily_trend = dict(cursor.fetchall())
                
                return {
                    'hourly_distribution': hourly_stats,
                    'weekly_distribution': daily_stats,
                    'daily_trend': daily_trend
                }
        except Exception as e:
            logger.error(f"Error getting time statistics: {e}")
            return {}
            
    def _get_location_statistics(self):
        """Get location-based analytics"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Accuracy distribution
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN accuracy < 10 THEN 'very_high'
                            WHEN accuracy < 50 THEN 'high'
                            WHEN accuracy < 100 THEN 'medium'
                            ELSE 'low'
                        END as accuracy_level,
                        COUNT(*) as count
                    FROM location_data 
                    WHERE accuracy IS NOT NULL
                    GROUP BY accuracy_level
                ''')
                accuracy_distribution = dict(cursor.fetchall())
                
                # Average accuracy by template
                cursor.execute('''
                    SELECT s.template, AVG(l.accuracy) as avg_accuracy
                    FROM sessions s
                    JOIN location_data l ON s.id = l.session_id
                    WHERE l.accuracy IS NOT NULL
                    GROUP BY s.template
                ''')
                template_accuracy = {template: round(acc, 2) for template, acc in cursor.fetchall()}
                
                return {
                    'accuracy_distribution': accuracy_distribution,
                    'template_accuracy': template_accuracy
                }
        except Exception as e:
            logger.error(f"Error getting location statistics: {e}")
            return {}
            
    def _get_device_statistics(self):
        """Get device-based analytics"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Platform distribution
                cursor.execute('''
                    SELECT platform, COUNT(*) as count
                    FROM device_fingerprints 
                    WHERE platform IS NOT NULL
                    GROUP BY platform
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                platform_stats = dict(cursor.fetchall())
                
                # Language distribution
                cursor.execute('''
                    SELECT language, COUNT(*) as count
                    FROM device_fingerprints 
                    WHERE language IS NOT NULL
                    GROUP BY language
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                language_stats = dict(cursor.fetchall())
                
                # Timezone distribution
                cursor.execute('''
                    SELECT timezone, COUNT(*) as count
                    FROM device_fingerprints 
                    WHERE timezone IS NOT NULL
                    GROUP BY timezone
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                timezone_stats = dict(cursor.fetchall())
                
                return {
                    'platform_distribution': platform_stats,
                    'language_distribution': language_stats,
                    'timezone_distribution': timezone_stats
                }
        except Exception as e:
            logger.error(f"Error getting device statistics: {e}")
            return {}
            
    def export_csv(self):
        """Export data as CSV"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Session ID', 'IP Address', 'User Agent', 'Template', 'Created At',
                'Latitude', 'Longitude', 'Accuracy', 'Altitude', 'Heading', 'Speed',
                'Platform', 'Language', 'Timezone', 'Canvas Fingerprint'
            ])
            
            # Get data
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        s.id, s.ip_address, s.user_agent, s.template, s.created_at,
                        l.latitude, l.longitude, l.accuracy, l.altitude, l.heading, l.speed,
                        d.platform, d.language, d.timezone, d.canvas_fingerprint
                    FROM sessions s
                    LEFT JOIN location_data l ON s.id = l.session_id
                    LEFT JOIN device_fingerprints d ON s.id = d.session_id
                    ORDER BY s.created_at DESC
                ''')
                
                for row in cursor.fetchall():
                    writer.writerow(row)
                    
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=seeker_data.csv'}
            )
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return Response("Error exporting data", status=500)
            
    def export_json(self):
        """Export data as JSON"""
        try:
            data = []
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        s.id, s.ip_address, s.user_agent, s.template, s.created_at, s.status,
                        s.location_data, s.device_data, s.accuracy
                    FROM sessions s
                    ORDER BY s.created_at DESC
                ''')
                
                for row in cursor.fetchall():
                    session_data = {
                        'session_id': row['id'],
                        'ip_address': row['ip_address'],
                        'user_agent': row['user_agent'],
                        'template': row['template'],
                        'created_at': row['created_at'],
                        'status': row['status'],
                        'accuracy': row['accuracy']
                    }
                    
                    # Parse JSON fields
                    if row['location_data']:
                        try:
                            session_data['location'] = json.loads(row['location_data'])
                        except:
                            pass
                            
                    if row['device_data']:
                        try:
                            session_data['device'] = json.loads(row['device_data'])
                        except:
                            pass
                            
                    data.append(session_data)
                    
            return Response(
                json.dumps(data, indent=2),
                mimetype='application/json',
                headers={'Content-Disposition': 'attachment; filename=seeker_data.json'}
            )
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return Response("Error exporting data", status=500)
            
    def export_kml(self):
        """Export location data as KML for Google Earth"""
        try:
            # Create KML structure
            kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
            document = ET.SubElement(kml, 'Document')
            ET.SubElement(document, 'name').text = 'Seeker Location Data'
            
            # Add style for placemarks
            style = ET.SubElement(document, 'Style', id='seekerStyle')
            icon_style = ET.SubElement(style, 'IconStyle')
            icon = ET.SubElement(icon_style, 'Icon')
            ET.SubElement(icon, 'href').text = 'http://maps.google.com/mapfiles/kml/shapes/target.png'
            
            # Get location data
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        s.id, s.template, s.created_at,
                        l.latitude, l.longitude, l.accuracy, l.collected_at
                    FROM sessions s
                    JOIN location_data l ON s.id = l.session_id
                    WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
                    ORDER BY l.collected_at DESC
                ''')
                
                for row in cursor.fetchall():
                    placemark = ET.SubElement(document, 'Placemark')
                    ET.SubElement(placemark, 'name').text = f"Session {row['id'][:8]}"
                    ET.SubElement(placemark, 'styleUrl').text = '#seekerStyle'
                    
                    description = f"""
                    Template: {row['template']}
                    Accuracy: {row['accuracy']}m
                    Created: {row['created_at']}
                    Collected: {row['collected_at']}
                    """
                    ET.SubElement(placemark, 'description').text = description.strip()
                    
                    point = ET.SubElement(placemark, 'Point')
                    coordinates = f"{row['longitude']},{row['latitude']},0"
                    ET.SubElement(point, 'coordinates').text = coordinates
                    
            # Convert to string
            kml_string = ET.tostring(kml, encoding='unicode')
            
            return Response(
                kml_string,
                mimetype='application/vnd.google-earth.kml+xml',
                headers={'Content-Disposition': 'attachment; filename=seeker_locations.kml'}
            )
        except Exception as e:
            logger.error(f"Error exporting KML: {e}")
            return Response("Error exporting data", status=500)
            
    def generate_report(self):
        """Generate comprehensive analytics report"""
        stats = self.get_statistics()
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'summary': {
                'total_sessions': stats.get('total_sessions', 0),
                'successful_collections': stats.get('successful_collections', 0),
                'success_rate': stats.get('success_rate', 0),
                'average_accuracy': stats.get('avg_accuracy', 0)
            },
            'detailed_analytics': stats
        }
        
        return report
