import json
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import PhishingTemplate, AnalyticsEvent
from app import db

phishing_bp = Blueprint('phishing', __name__)

@phishing_bp.route('/')
def templates():
    """View phishing templates"""
    templates = db.session.query(PhishingTemplate).filter_by(is_active=True).order_by(PhishingTemplate.created_at.desc()).all()
    
    # Track page view
    event = AnalyticsEvent(
        event_type='phishing_templates_view',
        event_data=json.dumps({'page': 'templates'}),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        session_id=session.get('session_id')
    )
    db.session.add(event)
    db.session.commit()
    
    return render_template('phishing/templates.html', templates=templates)

@phishing_bp.route('/create')
def create_template():
    """Create new phishing template"""
    return render_template('phishing/create_template.html')

@phishing_bp.route('/create', methods=['POST'])
def save_template():
    """Save new phishing template"""
    name = request.form.get('name', '').strip()
    template_type = request.form.get('template_type', '').strip()
    html_content = request.form.get('html_content', '').strip()
    css_content = request.form.get('css_content', '').strip()
    js_content = request.form.get('js_content', '').strip()
    
    if not name or not template_type or not html_content:
        flash('Name, type, and HTML content are required', 'error')
        return redirect(url_for('phishing.create_template'))
    
    try:
        template = PhishingTemplate(
            name=name,
            template_type=template_type,
            html_content=html_content,
            css_content=css_content,
            js_content=js_content
        )
        db.session.add(template)
        
        # Track template creation
        event = AnalyticsEvent(
            event_type='template_created',
            event_data=json.dumps({'name': name, 'type': template_type}),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            session_id=session.get('session_id')
        )
        db.session.add(event)
        db.session.commit()
        
        flash('Template created successfully', 'success')
        return redirect(url_for('phishing.templates'))
    except Exception as e:
        flash(f'Error creating template: {str(e)}', 'error')
        return redirect(url_for('phishing.create_template'))

@phishing_bp.route('/preview/<int:template_id>')
def preview_template(template_id):
    """Preview a phishing template"""
    template = db.session.get(PhishingTemplate, template_id)
    if not template:
        from flask import abort
        abort(404)
    
    # Track template preview
    event = AnalyticsEvent(
        event_type='template_preview',
        event_data=json.dumps({'template_id': template_id, 'name': template.name}),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        session_id=session.get('session_id')
    )
    db.session.add(event)
    db.session.commit()
    
    return render_template('phishing/preview.html', template=template)

@phishing_bp.route('/delete/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    """Delete a phishing template"""
    template = db.session.get(PhishingTemplate, template_id)
    if not template:
        from flask import abort
        abort(404)
    template.is_active = False
    
    # Track template deletion
    event = AnalyticsEvent(
        event_type='template_deleted',
        event_data=json.dumps({'template_id': template_id, 'name': template.name}),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        session_id=session.get('session_id')
    )
    db.session.add(event)
    db.session.commit()
    
    flash('Template deleted successfully', 'success')
    return redirect(url_for('phishing.templates'))
