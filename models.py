from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to searches
    searches = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    search_type = db.Column(db.String(50), nullable=False)  # username, domain, ip, email, phone
    query = db.Column(db.String(255), nullable=False)
    results = db.Column(db.Text)  # JSON string of results
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(255))

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    search_type = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, default=1)
    
    __table_args__ = (db.UniqueConstraint('date', 'search_type', name='_date_search_type_uc'),)

class PhishingTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_html = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class SeekerSession(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    visits = db.Column(db.Integer, default=0)
    
    # Relationships
    locations = db.relationship('SeekerLocation', backref='session', lazy=True, cascade='all, delete-orphan')
    devices = db.relationship('SeekerDevice', backref='session', lazy=True, cascade='all, delete-orphan')

class SeekerLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32), db.ForeignKey('seeker_session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    altitude = db.Column(db.Float)
    speed = db.Column(db.Float)
    heading = db.Column(db.Float)
    ip_address = db.Column(db.String(45))

class SeekerDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32), db.ForeignKey('seeker_session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_agent = db.Column(db.Text)
    screen_resolution = db.Column(db.String(20))
    timezone = db.Column(db.String(50))
    language = db.Column(db.String(10))
    platform = db.Column(db.String(50))
    cpu_cores = db.Column(db.Integer)
    memory = db.Column(db.Float)
    gpu = db.Column(db.Text)
    canvas_fingerprint = db.Column(db.Text)
    webgl_fingerprint = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
