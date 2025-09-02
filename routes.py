from app import app, db
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from models import SearchHistory, Analytics, PhishingTemplate
from osint_tools import OSINTTools
from web_scraper import get_website_text_content
from datetime import datetime, date
import json
import logging

osint = OSINTTools()

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500
