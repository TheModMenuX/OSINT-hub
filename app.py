import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///osint_tool.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Register blueprints
from routes.dashboard import dashboard_bp
from routes.osint import osint_bp
from routes.phishing import phishing_bp
from routes.analytics import analytics_bp

app.register_blueprint(dashboard_bp)
app.register_blueprint(osint_bp, url_prefix='/osint')
app.register_blueprint(phishing_bp, url_prefix='/phishing')
app.register_blueprint(analytics_bp, url_prefix='/analytics')

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
