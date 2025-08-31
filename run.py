#!/usr/bin/env python3
"""
Main entry point for the Snowsports Program Manager application.

This module initializes and runs the Flask application.
"""
import os
import sys
import click
from flask import current_app
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate

def make_shell_context():
    ""
    Create a shell context that adds database instance and models to the shell session.
    """
    return {
        'db': db,
        'User': User,
        'Role': Role
    }

def register_commands(app):
    ""
    Register custom CLI commands.
    ""
    @app.cli.command('init-db')
    @click.option('--admin-email', default='admin@example.com', help='Admin email')
    @click.option('--admin-password', default=None, help='Admin password')
    def init_db(admin_email, admin_password):
        """Initialize the database and create an admin user."""
        with app.app_context():
            # Create database tables
            db.create_all()
            
            # Create roles if they don't exist
            Role.insert_roles()
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(email=admin_email).first()
            if admin is None:
                admin = User(
                    username='admin',
                    email=admin_email,
                    confirmed=True,
                    is_admin=True
                )
                if admin_password:
                    admin.set_password(admin_password)
                else:
                    # Generate a random password if not provided
                    import secrets
                    admin_password = secrets.token_urlsafe(12)
                    admin.set_password(admin_password)
                
                # Add admin role
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    admin.roles.append(admin_role)
                
                db.session.add(admin)
                db.session.commit()
                
                print(f"Created admin user with email '{admin_email}' and password '{admin_password}'")
                print("IMPORTANT: Change this password after first login!")
            else:
                print(f"Admin user with email '{admin_email}' already exists.")
    
    @app.cli.command('create-user')
    @click.argument('email')
    @click.option('--username', default=None, help='Username (defaults to email prefix)')
    @click.option('--password', default=None, help='Password (random if not provided)')
    @click.option('--admin', is_flag=True, help='Make user an admin')
    def create_user(email, username, password, admin):
        """Create a new user."""
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if user is not None:
                print(f"Error: User with email '{email}' already exists.")
                return
            
            if username is None:
                username = email.split('@')[0]
            
            if password is None:
                import secrets
                password = secrets.token_urlsafe(12)
            
            user = User(
                username=username,
                email=email,
                confirmed=True,
                is_admin=admin
            )
            user.set_password(password)
            
            # Add user role
            user_role = Role.query.filter_by(name='user').first()
            if user_role:
                user.roles.append(user_role)
            
            # Add admin role if requested
            if admin:
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role and admin_role not in user.roles:
                    user.roles.append(admin_role)
            
            db.session.add(user)
            db.session.commit()
            
            print(f"Created user with email '{email}' and password '{password}'")
            if admin:
                print("This user has admin privileges.")

# Create the Flask application
app = create_app(os.getenv('FLASK_ENV') or 'development')

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Register shell context
app.shell_context_processor(make_shell_context)

# Register CLI commands
register_commands(app)

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(host='0.0.0.0', port=port)
