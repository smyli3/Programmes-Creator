"""
WSGI config for Snowsports Program Manager.

This module contains the WSGI application used by the application server.
It exposes a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os
from app import create_app

# Set the default settings module for the 'app' to use
os.environ.setdefault('FLASK_ENV', 'production')

# Create the Flask application instance
application = create_app()

if __name__ == "__main__":
    # This block is only used when running the application directly,
    # e.g., with `python wsgi.py`. In production, a WSGI server like
    # Gunicorn will import this module and use the `application` object.
    application.run()
