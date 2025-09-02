from flask import render_template, request, jsonify, flash, redirect, url_for, session
from app import app, db
from models import SearchHistory, Bookmark, ApiCache
from osint_tools import OSINTTools
import json
import logging

osint = OSINTTools()

@app.route('/')
def index():
    """Main dashboard with tool overview"""
    recent_searches = db.session.query(SearchHistory).order_by(SearchHistory.timestamp.desc()).limit(5).all()
    bookmarks = db.session.query(Bookmark).order_by(Bookmark.timestamp.desc()).limit(5).all()
    return render_template('index.html', recent_searches=recent_searches, bookmarks=bookmarks)

@app.route('/ip-lookup', methods=['GET', 'POST'])
def ip_lookup():
    """IP Geolocation and analysis"""
    if request.method == 'POST':
        ip_address = request.form.get('ip_address', '').strip()
        
        if not ip_address:
            flash('Please enter a valid IP address', 'error')
            return render_template('ip_lookup.html')
        
        try:
            # Perform IP lookup
            result = osint.ip_geolocation(ip_address)
            
            # Save to history
            history = SearchHistory(
                search_type='ip_lookup',
                query=ip_address,
                results=json.dumps(result),
                ip_address=request.remote_addr
            )
            db.session.add(history)
            db.session.commit()
            
            return render_template('results.html', 
                                 search_type='IP Lookup', 
                                 query=ip_address, 
                                 results=result)
        
        except Exception as e:
            logging.error(f"IP lookup error: {str(e)}")
            flash(f'Error performing IP lookup: {str(e)}', 'error')
    
    return render_template('ip_lookup.html')

@app.route('/email-search', methods=['GET', 'POST'])
def email_search():
    """Email search and validation"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter a valid email address', 'error')
            return render_template('email_search.html')
        
        try:
            # Perform email search
            result = osint.email_search(email)
            
            # Save to history
            history = SearchHistory(
                search_type='email_search',
                query=email,
                results=json.dumps(result),
                ip_address=request.remote_addr
            )
            db.session.add(history)
            db.session.commit()
            
            return render_template('results.html', 
                                 search_type='Email Search', 
                                 query=email, 
                                 results=result)
        
        except Exception as e:
            logging.error(f"Email search error: {str(e)}")
            flash(f'Error performing email search: {str(e)}', 'error')
    
    return render_template('email_search.html')

@app.route('/domain-analysis', methods=['GET', 'POST'])
def domain_analysis():
    """Domain WHOIS and analysis"""
    if request.method == 'POST':
        domain = request.form.get('domain', '').strip()
        
        if not domain:
            flash('Please enter a valid domain', 'error')
            return render_template('domain_analysis.html')
        
        try:
            # Perform domain analysis
            result = osint.domain_analysis(domain)
            
            # Save to history
            history = SearchHistory(
                search_type='domain_analysis',
                query=domain,
                results=json.dumps(result),
                ip_address=request.remote_addr
            )
            db.session.add(history)
            db.session.commit()
            
            return render_template('results.html', 
                                 search_type='Domain Analysis', 
                                 query=domain, 
                                 results=result)
        
        except Exception as e:
            logging.error(f"Domain analysis error: {str(e)}")
            flash(f'Error performing domain analysis: {str(e)}', 'error')
    
    return render_template('domain_analysis.html')

@app.route('/username-search', methods=['GET', 'POST'])
def username_search():
    """Username search across platforms"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Please enter a valid username', 'error')
            return render_template('username_search.html')
        
        try:
            # Perform username search
            result = osint.username_search(username)
            
            # Save to history
            history = SearchHistory(
                search_type='username_search',
                query=username,
                results=json.dumps(result),
                ip_address=request.remote_addr
            )
            db.session.add(history)
            db.session.commit()
            
            return render_template('results.html', 
                                 search_type='Username Search', 
                                 query=username, 
                                 results=result)
        
        except Exception as e:
            logging.error(f"Username search error: {str(e)}")
            flash(f'Error performing username search: {str(e)}', 'error')
    
    return render_template('username_search.html')

@app.route('/phone-lookup', methods=['GET', 'POST'])
def phone_lookup():
    """Phone number lookup"""
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        
        if not phone:
            flash('Please enter a valid phone number', 'error')
            return render_template('phone_lookup.html')
        
        try:
            # Perform phone lookup
            result = osint.phone_lookup(phone)
            
            # Save to history
            history = SearchHistory(
                search_type='phone_lookup',
                query=phone,
                results=json.dumps(result),
                ip_address=request.remote_addr
            )
            db.session.add(history)
            db.session.commit()
            
            return render_template('results.html', 
                                 search_type='Phone Lookup', 
                                 query=phone, 
                                 results=result)
        
        except Exception as e:
            logging.error(f"Phone lookup error: {str(e)}")
            flash(f'Error performing phone lookup: {str(e)}', 'error')
    
    return render_template('phone_lookup.html')

@app.route('/bookmark', methods=['POST'])
def add_bookmark():
    """Add search to bookmarks"""
    try:
        data = request.get_json()
        bookmark = Bookmark(
            title=data.get('title'),
            search_type=data.get('search_type'),
            query=data.get('query'),
            results=data.get('results'),
            notes=data.get('notes', '')
        )
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bookmark added successfully'})
    except Exception as e:
        logging.error(f"Bookmark error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/history')
def search_history():
    """View search history"""
    searches = db.session.query(SearchHistory).order_by(SearchHistory.timestamp.desc()).limit(50).all()
    return render_template('history.html', searches=searches)

@app.route('/bookmarks')
def bookmarks():
    """View bookmarks"""
    user_bookmarks = db.session.query(Bookmark).order_by(Bookmark.timestamp.desc()).all()
    return render_template('bookmarks.html', bookmarks=user_bookmarks)

@app.route('/export/<int:search_id>')
def export_results(search_id):
    """Export search results"""
    search = db.session.get(SearchHistory, search_id)
    if not search:
        return jsonify({'error': 'Search not found'}), 404
    return jsonify({
        'search_type': search.search_type,
        'query': search.query,
        'results': json.loads(search.results) if search.results else {},
        'timestamp': search.timestamp.isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
