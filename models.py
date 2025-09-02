from datetime import datetime
from app import db

class SearchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_type = db.Column(db.String(50), nullable=False)  # username, domain, email
    query = db.Column(db.String(255), nullable=False)
    results = db.Column(db.Text)  # JSON string of results
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

class PhishingTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # login, survey, etc
    html_content = db.Column(db.Text, nullable=False)
    css_content = db.Column(db.Text)
    js_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class AnalyticsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # search, template_view, etc
    event_data = db.Column(db.Text)  # JSON string of event details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))

class Session(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    page_views = db.Column(db.Integer, default=0)
