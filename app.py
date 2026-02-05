# app.py

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_session import Session
from models.db import db
import os

# Import Flask-Dance and Google integration
from flask_dance.contrib.google import make_google_blueprint, google
from flask_migrate import Migrate

# Import all route blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.lahan import lahan_bp
from routes.monitoring import monitoring_bp
from routes.pemeliharaan import pemeliharaan_bp
from routes.hama import hama_bp
from routes.lingkungan import lingkungan_bp
from routes.permasalahan import permasalahan_bp
from routes.api import api_bp
from routes.admin import admin_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Setup UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup session storage
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# NOTE: Retrieve Google credentials from environment variables
# Ensure these variables exist in your .env file
google_client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
google_client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")

if google_client_id and google_client_secret:
    google_bp = make_google_blueprint(
        client_id=google_client_id,
        client_secret=google_client_secret,
        scope=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    )
    app.register_blueprint(google_bp, url_prefix='/google')

# Register application blueprints
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(dashboard_bp, url_prefix='/')
app.register_blueprint(lahan_bp, url_prefix='/lahan')
app.register_blueprint(monitoring_bp, url_prefix='/monitoring')
app.register_blueprint(pemeliharaan_bp, url_prefix='/pemeliharaan')
app.register_blueprint(hama_bp, url_prefix='/hama')
app.register_blueprint(lingkungan_bp, url_prefix='/lingkungan')
app.register_blueprint(permasalahan_bp, url_prefix='/permasalahan')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Register Google OAuth blueprint
app.register_blueprint(google_bp, url_prefix='/google')

# Create database tables if they do not exist
#with app.app_context():
#    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
