import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    # App settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123-change-this-in-production'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'change-this-in-production'
    
    # Database
    # Normalize legacy postgres:// URLs used by some providers
    _database_url = os.environ.get('DATABASE_URL')
    if _database_url and _database_url.startswith('postgres://'):
        _database_url = _database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _database_url or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Security settings
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome to Snowsports Program Manager'
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = 'Your password has been reset'
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = 'Your password has been changed'
    SECURITY_EMAIL_SUBJECT_CONFIRM = 'Please confirm your email'
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = 'Password reset instructions'
    
    # Rate limiting
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Pagination
    PAGINATION_PER_PAGE = 20
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@snowsports.example.com')
    MAIL_SUBJECT_PREFIX = '[Snowsports] '
    
    # Application settings
    APP_NAME = 'Snowsports Program Manager'
    APP_ADMIN = os.environ.get('APP_ADMIN')
    
    @staticmethod
    def init_app(app):
        """Initialize configuration."""
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app-dev.db')
    SQLALCHEMY_ECHO = True
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False  # Set to True to disable sending emails in development
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier form testing


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory SQLite for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    MAIL_SUPPRESS_SEND = True  # Don't send emails during testing
    SERVER_NAME = 'localhost:5000'  # Required for test client
    

class ProductionConfig(Config):
    """Production configuration."""
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Disable SQLAlchemy event system for better performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Rate limiting
    RATELIMIT_DEFAULT = '1000 per day;100 per hour'
    
    # Email settings
    MAIL_DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Email configuration for backward compatibility
class EmailConfig:
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@snowsports.example.com')
