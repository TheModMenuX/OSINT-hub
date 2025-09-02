import json
from flask import Blueprint, render_template, request, session
from models import SearchResult, AnalyticsEvent, Session
from app import db
from datetime import datetime, timedelta
import uuid

dashboard_bp = Blueprint('dashboard', __name__)

def get_or_create_session():
    """Get or create a session for analytics tracking"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        
    session_record = db.session.get(Session, session['session_id'])
    if not session_record:
        session_record = Session(
            id=session['session_id'],
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(session_record)
    else:
        session_record.last_activity = datetime.utcnow()
        session_record.page_views += 1
    
    db.session.commit()
    return session_record

@dashboard_bp.route('/')
def index():
    """Main dashboard page"""
    get_or_create_session()
    
    # Track page view
    event = AnalyticsEvent(
        event_type='page_view',
        event_data=json.dumps({'page': 'dashboard'}),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        session_id=session.get('session_id')
    )
    db.session.add(event)
    db.session.commit()
    
    # Get recent search statistics
    recent_searches = db.session.query(SearchResult).filter(
        SearchResult.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    username_searches = db.session.query(SearchResult).filter_by(search_type='username').count()
    domain_searches = db.session.query(SearchResult).filter_by(search_type='domain').count()
    email_searches = db.session.query(SearchResult).filter_by(search_type='email').count()
    
    stats = {
        'recent_searches': recent_searches,
        'username_searches': username_searches,
        'domain_searches': domain_searches,
        'email_searches': email_searches,
        'total_searches': username_searches + domain_searches + email_searches
    }
    
    return render_template('dashboard.html', stats=stats)
