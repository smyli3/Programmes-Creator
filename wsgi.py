#!/usr/bin/env python3
"""
WSGI config for Snowsports Program Manager.

This module contains the WSGI application used by the application server.
It exposes a module-level variable named ``application``.

For more information on WSGI configuration, see:
https://flask.palletsprojects.com/en/2.3.x/deploying/wsgi-standalone/
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Add the project directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the application factory
from app import create_app

# Set the default environment to production for safety
os.environ.setdefault('FLASK_ENV', 'production')

# Create the application instance
application = create_app()

# Configure logging for production
if not application.debug and not application.testing:
    # Ensure the log directory exists
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a file handler for errors
    error_log = os.path.join(log_dir, 'error.log')
    file_handler = RotatingFileHandler(
        error_log, 
        maxBytes=10240,  # 10KB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    application.logger.addHandler(file_handler)
    
    # Set the application logger level
    application.logger.setLevel(logging.INFO)
    application.logger.info('Snowsports Program Manager startup')

# This block is only used when running the application directly
if __name__ == "__main__":
    # In production, a WSGI server like Gunicorn will import this module
    # and use the `application` object directly.
    # This is only for development/testing.
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
