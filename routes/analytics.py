import json
from flask import Blueprint, render_template, request
from models import AnalyticsEvent, SearchResult, Session
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
def dashboard():
    """Analytics dashboard"""
    # Get date range from query params
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Overall statistics
    total_searches = db.session.query(SearchResult).count()
    recent_searches = db.session.query(SearchResult).filter(SearchResult.timestamp >= start_date).count()
    total_sessions = db.session.query(Session).count()
    active_sessions = db.session.query(Session).filter(Session.last_activity >= start_date).count()
    
    # Search type breakdown
    search_types = db.session.query(
        SearchResult.search_type,
        func.count(SearchResult.id).label('count')
    ).filter(SearchResult.timestamp >= start_date).group_by(SearchResult.search_type).all()
    
    # Daily search activity
    daily_activity = db.session.query(
        func.date(SearchResult.timestamp).label('date'),
        func.count(SearchResult.id).label('searches')
    ).filter(SearchResult.timestamp >= start_date).group_by(
        func.date(SearchResult.timestamp)
    ).order_by('date').all()
    
    # Top search queries
    top_queries = db.session.query(
        SearchResult.query,
        SearchResult.search_type,
        func.count(SearchResult.id).label('count')
    ).filter(SearchResult.timestamp >= start_date).group_by(
        SearchResult.query, SearchResult.search_type
    ).order_by(desc('count')).limit(10).all()
    
    # Event type breakdown
    event_types = db.session.query(
        AnalyticsEvent.event_type,
        func.count(AnalyticsEvent.id).label('count')
    ).filter(AnalyticsEvent.timestamp >= start_date).group_by(
        AnalyticsEvent.event_type
    ).order_by(desc('count')).all()
    
    # Recent activity
    recent_events = db.session.query(AnalyticsEvent).filter(
        AnalyticsEvent.timestamp >= start_date
    ).order_by(desc(AnalyticsEvent.timestamp)).limit(20).all()
    
    stats = {
        'total_searches': total_searches,
        'recent_searches': recent_searches,
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'search_types': [{'type': st[0], 'count': st[1]} for st in search_types],
        'daily_activity': [{'date': da[0].strftime('%Y-%m-%d'), 'searches': da[1]} for da in daily_activity],
        'top_queries': [{'query': tq[0], 'type': tq[1], 'count': tq[2]} for tq in top_queries],
        'event_types': [{'type': et[0], 'count': et[1]} for et in event_types],
        'recent_events': recent_events,
        'date_range': days
    }
    
    return render_template('analytics/dashboard.html', stats=stats)
