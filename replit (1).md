# Overview

Enhanced Seeker v2.0 is an advanced geolocation tool that combines social engineering techniques with modern web technologies to gather precise location data and device fingerprinting information. The application features a comprehensive web dashboard for real-time monitoring, multiple template-based phishing pages mimicking popular services (Instagram, WhatsApp, Snapchat, TikTok, Uber, Netflix, Spotify, Amazon), and advanced analytics capabilities. It's designed as an educational and research tool for understanding geolocation vulnerabilities and social engineering attack vectors.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

The application follows a Flask-based web architecture with real-time capabilities through WebSocket integration. The main components include:

**Backend Architecture:**
- Flask web framework serving as the core application server
- SQLite database for persistent storage of session data, location information, and device fingerprints
- WebSocket integration using Flask-SocketIO for real-time dashboard updates
- Modular utility system with separate modules for fingerprinting, analytics, tunneling, and webhook management

**Database Design:**
- Session tracking with comprehensive metadata storage
- Location data with accuracy metrics and collection timestamps  
- Device fingerprinting data including browser details, hardware specs, and unique identifiers
- Analytics tables for time-based and geographical reporting

**Frontend Architecture:**
- Bootstrap-based responsive web interface
- Real-time dashboard with live session monitoring
- Template management system for social engineering pages
- JavaScript-based device fingerprinting using Canvas, WebGL, and audio fingerprinting
- Chart visualization for analytics reporting

**Security and Privacy Controls:**
- Rate limiting to prevent abuse
- Configurable data retention policies
- Optional webhook integration for external notifications
- Telegram bot integration for real-time alerts

**Template System:**
- Eight pre-built social engineering templates mimicking popular services
- Dynamic template generation with customizable parameters
- Responsive design optimized for mobile devices
- Geolocation API integration with fallback mechanisms

# External Dependencies

**Core Web Framework:**
- Flask web framework with SocketIO for real-time communication
- Bootstrap CSS framework for responsive UI design
- jQuery for client-side JavaScript functionality

**Tunneling Services:**
- ngrok for secure tunnel creation and public URL exposure
- Serveo as alternative tunneling service
- localtunnel for additional tunnel options

**Database:**
- SQLite for local data persistence and session management

**Notification Systems:**
- Telegram Bot API for real-time notifications and alerts
- Webhook support for custom external integrations

**Analytics and Visualization:**
- Chart.js or similar charting libraries for data visualization
- CSV/JSON/KML export capabilities for data analysis

**Geolocation Services:**
- HTML5 Geolocation API as primary location source
- IP-based geolocation as fallback mechanism
- Multiple accuracy threshold configurations

The application is designed to be self-contained with minimal external dependencies while providing extensive integration options for advanced users and researchers.