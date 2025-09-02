# Overview

This repository contains two main applications: an OSINT Intelligence Platform and Enhanced Seeker v2.0. The OSINT platform is a comprehensive open-source intelligence gathering tool built with Flask that provides IP geolocation, email validation, domain analysis, phone lookup, and username search capabilities. Enhanced Seeker is an advanced geolocation tool with real-time dashboard functionality that uses social engineering templates to collect precise location data and device fingerprinting information.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

**OSINT Platform Architecture:**
- Flask-based web application with SQLAlchemy ORM for database operations
- SQLite database for storing search history, bookmarks, and API cache
- Modular design with separate modules for OSINT tools, web scraping, and route handling
- Bootstrap-based responsive frontend with dark theme optimized for cybersecurity professionals
- Integration with external APIs (IPGeolocation, Hunter, Shodan) for comprehensive intelligence gathering
- Built-in rate limiting and caching mechanisms to optimize API usage

**Enhanced Seeker Architecture:**
- Flask web framework with Socket.IO for real-time WebSocket communication
- SQLite database with comprehensive session tracking and analytics storage
- Modular utility system including device fingerprinting, analytics engine, tunnel management, and webhook integration
- Eight pre-built social engineering templates mimicking popular services (Instagram, WhatsApp, Snapchat, TikTok, Uber, Netflix, Spotify, Amazon)
- Advanced client-side fingerprinting using Canvas, WebGL, and audio fingerprinting techniques
- Real-time dashboard with live session monitoring and data visualization

**Database Design:**
- OSINT Platform: Simple schema with SearchHistory, Bookmark, and ApiCache tables
- Enhanced Seeker: Complex schema with sessions, location data, device fingerprints, and analytics tables with time-based reporting capabilities

**Security and Privacy:**
- Rate limiting mechanisms to prevent API abuse
- Configurable data retention policies
- Optional webhook integration for external notifications
- Environment variable configuration for sensitive API keys and settings

# External Dependencies

**Core Web Frameworks:**
- Flask web framework with SQLAlchemy ORM
- Flask-SocketIO for real-time WebSocket communication
- Bootstrap CSS framework for responsive UI design
- jQuery and JavaScript for client-side functionality

**Database:**
- SQLite for local data storage (both applications support environment-based database URL configuration)

**OSINT APIs and Services:**
- IPGeolocation API for IP address analysis
- Hunter.io API for email validation and search
- Shodan API for network security scanning
- WHOIS services for domain information
- DNS resolution libraries

**External Integrations:**
- Discord webhook support for alerts and notifications
- Telegram bot integration for real-time notifications
- Tunnel services (ngrok, serveo, localtunnel) for external access
- Web scraping capabilities using trafilatura library

**Development Tools:**
- Python-whois for domain analysis
- DNS resolver libraries for network investigation
- User-agent parsing libraries for device fingerprinting
- Requests library for HTTP operations and API interactions