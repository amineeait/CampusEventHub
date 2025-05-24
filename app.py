import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config.Config')

# Set secret key from environment variable
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure proxy fix for proper URL generation
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize SQLAlchemy with the app
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models for table creation
with app.app_context():
    from models import User, Club, Event, Registration, Attendance, Rating, Photo, Reminder
    db.create_all()
    logging.info("Database tables created")

# Import user loader function
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
