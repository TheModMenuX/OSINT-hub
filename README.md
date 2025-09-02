# Enhanced Seeker v2.0

**Advanced Geolocation Tool with Real-time Dashboard and Enhanced Analytics**

⚠️ **EDUCATIONAL/RESEARCH USE ONLY** ⚠️

## Overview

Enhanced Seeker is an upgraded version of the popular seeker geolocation tool, featuring a comprehensive web dashboard, advanced device fingerprinting, real-time analytics, and multiple social engineering templates. This tool demonstrates modern web-based location tracking capabilities and serves as both a penetration testing resource and cybersecurity awareness tool.

## Features

### 🎯 Core Functionality
- **High-Precision Geolocation**: Accurate location tracking using GPS, WiFi, and cell tower data
- **Multiple Templates**: 8 social engineering templates mimicking popular services
- **Real-time Dashboard**: Live monitoring of active sessions and data collection
- **Advanced Analytics**: Comprehensive reporting with charts and statistics
- **Device Fingerprinting**: Detailed device and browser information collection

### 🌐 Web Dashboard
- **Live Session Monitoring**: Real-time WebSocket updates for active sessions
- **Template Management**: Easy switching between different social engineering templates
- **Analytics Dashboard**: Visual charts and metrics for collected data
- **Session History**: Complete audit trail of all interactions
- **Export Capabilities**: CSV, JSON, and KML export formats

### 🔧 Technical Features
- **Tunnel Management**: Integrated support for ngrok, serveo, and localtunnel
- **Webhook Integration**: Forward collected data to external services
- **Database Storage**: SQLite database for persistent data storage
- **Advanced Fingerprinting**: Canvas, WebGL, audio, and font fingerprinting
- **Rate Limiting**: Built-in protection against abuse
- **Telegram Integration**: Real-time notifications via Telegram bot

### 📱 Social Engineering Templates
1. **Instagram** - Location sharing for "nearby friends"
2. **WhatsApp** - Location verification for security
3. **Snapchat** - Snap Map location sharing
4. **TikTok** - Local content discovery
5. **Uber** - Pickup location confirmation
6. **Netflix** - Regional content access
7. **Spotify** - Concert and event discovery
8. **Amazon** - Delivery location verification

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git

### Quick Install
```bash
# Clone the repository
git clone https://github.com/enhanced-seeker/enhanced-seeker.git
cd enhanced-seeker

# Run the installation script
chmod +x install.sh
./install.sh

# Start Enhanced Seeker
python3 app.py
