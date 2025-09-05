from flask import Blueprint

# Create blueprint
auth = Blueprint('auth', __name__)

# Import routes after creating the blueprint to avoid circular imports
from . import routes
