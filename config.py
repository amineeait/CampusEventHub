import os

class Config:
    # Flask configuration
    DEBUG = True
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev_secret_key")
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
