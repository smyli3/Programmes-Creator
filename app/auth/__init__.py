from flask import Blueprint

# Expose blueprint as `bp` per rebuild guide
bp = Blueprint('auth', __name__)

# Import routes after creating the blueprint to avoid circular imports
from . import routes
