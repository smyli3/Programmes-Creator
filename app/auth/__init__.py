from flask import Blueprint
from flask_login import LoginManager
from ..models import User

# Create login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Create blueprint
auth = Blueprint('auth', __name__)

# Import routes after creating the blueprint to avoid circular imports
from . import routes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
