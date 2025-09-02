import json
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import SearchResult, AnalyticsEvent
from services.osint_tools import OSINTTools
from app import db
from datetime import datetime

osint_bp = Blueprint('osint', __name__)

@osint_bp.route('/username')
def username_search():
    """Username search page"""
    return render_template('osint/username_search.html')

@osint_bp.route('/domain')
def domain_search():
    """Domain search page"""
    return render_template('osint/domain_search.html')

@osint_bp.route('/email')
def email_search():
    """Email search page"""
    return render_template('osint/email_search.html')

@osint_bp.route('/search/username', methods=['POST'])
def search_username():
    """Perform username search"""
    username = request.form.get('username', '').strip()
    if not username:
        flash('Please enter a username to search', 'error')
        return redirect(url_for('osint.username_search'))
    
    # Track search event
    event = AnalyticsEvent(
        event_type='username_search',
        event_data=json.dumps({'username': username}),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        session_id=session.get('session_id')
    )
    db.session.add(event)
    
    try:
        osint_tools = OSINTTools()
        results = osint_tools.search_username(username)
        
        # Store search results
        search_result = SearchResult(
            search_type='username',
            query=username,
            results=json.dumps(results),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(search_result)
        db.session.commit()
        
        return render_template('osint/results.html', 
                             search_type='Username', 
                             query=username, 
                             results=results)
    except Exception as e:
        flash(f'Search failed: {str(e)}', 'error')
        return redirect(url_for('osint.username_search'))

@osint_bp.route('/search/domain', methods=['POST'])
def search_domain():
    """Perform domain search"""
    domain = request.form.get('domain', '').strip()
    if not domain:
        flash('Please enter a domain to search', 'error')
        return redirect(url_for('osint.domain_search'))
    
    # Track search event
    event = AnalyticsEvent(
        event_type='domain_search',
        event_data=json.dumps({'domain': domain}),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        session_id=session.get('session_id')
    )
    db.session.add(event)
    
    try:
        osint_tools = OSINTTools()
        results = osint_tools.search_domain(domain)
        
        # Store search results
        search_result = SearchResult(
            search_type='domain',
            query=domain,
            results=json.dumps(results),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(search_result)
        db.session.commit()
        
        return render_template('osint/results.html', 
                             search_type='Domain', 
                             query=domain, 
                             results=results)
    except Exception as e:
        flash(f'Search failed: {str(e)}', 'error')
        return redirect(url_for('osint.domain_search'))

@osint_bp.route('/search/email', methods=['POST'])
def search_email():
    """Perform email search"""
    email = request.form.get('email', '').strip()
    if not email:
        flash('Please enter an email to search', 'error')
        return redirect(url_for('osint.email_search'))
    
    # Track search event
    event = AnalyticsEvent(
        event_type='email_search',
        event_data=json.dumps({'email': email}),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        session_id=session.get('session_id')
    )
    db.session.add(event)
    
    try:
        osint_tools = OSINTTools()
        results = osint_tools.search_email(email)
        
        # Store search results
        search_result = SearchResult(
            search_type='email',
            query=email,
            results=json.dumps(results),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(search_result)
        db.session.commit()
        
        return render_template('osint/results.html', 
                             search_type='Email', 
                             query=email, 
                             results=results)
    except Exception as e:
        flash(f'Search failed: {str(e)}', 'error')
        return redirect(url_for('osint.email_search'))

@osint_bp.route('/history')
def search_history():
    """View search history"""
    page = request.args.get('page', 1, type=int)
    searches = db.session.query(SearchResult).order_by(SearchResult.timestamp.desc()).limit(20).offset((page-1)*20).all()
    return render_template('osint/history.html', searches=searches)
