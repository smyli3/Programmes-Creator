import os
import click
from flask import Flask, render_template
from .extensions import db, migrate, login_manager, csrf, mail
from config import config

def create_db():
    """Create database tables."""
    db.create_all()

def drop_db():
    """Drop all database tables."""
    db.drop_all()

def register_cli(app):
    """Register custom Flask CLI commands for admin and DB tasks."""
    @app.cli.command('init-db')
    @click.option('--admin-email', default='admin@example.com', help='Admin email')
    @click.option('--admin-password', default=None, help='Admin password')
    def init_db_cmd(admin_email, admin_password):
        """Initialize the database, insert roles, and create an admin user."""
        from .models import User, Role
        with app.app_context():
            db.create_all()
            Role.insert_roles()
            admin = User.query.filter_by(email=admin_email).first()
            if admin is None:
                admin = User(
                    username=admin_email.split('@')[0],
                    email=admin_email,
                    is_admin=True
                )
                # set password
                if admin_password:
                    admin.set_password(admin_password)
                else:
                    import secrets
                    admin_password = secrets.token_urlsafe(12)
                    admin.set_password(admin_password)
                # attach admin role if exists
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    admin.roles.append(admin_role)
                db.session.add(admin)
                db.session.commit()
                click.echo(f"Created admin user '{admin_email}' with password '{admin_password}'")
                click.echo("IMPORTANT: Change this password after first login!")
            else:
                click.echo(f"Admin user with email '{admin_email}' already exists.")

    @app.cli.command('create-user')
    @click.argument('email')
    @click.option('--username', default=None, help='Username (defaults to email prefix)')
    @click.option('--password', default=None, help='Password (random if not provided)')
    @click.option('--admin', is_flag=True, help='Make user an admin')
    def create_user_cmd(email, username, password, admin):
        """Create a new user and optionally grant admin role."""
        from .models import User, Role
        with app.app_context():
            if User.query.filter_by(email=email).first():
                click.echo(f"Error: User with email '{email}' already exists.")
                return
            if username is None:
                username = email.split('@')[0]
            if password is None:
                import secrets
                password = secrets.token_urlsafe(12)
            user = User(
                username=username,
                email=email,
                is_admin=admin
            )
            user.set_password(password)
            user_role = Role.query.filter_by(name='user').first()
            if user_role:
                user.roles.append(user_role)
            if admin:
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role and admin_role not in user.roles:
                    user.roles.append(admin_role)
            db.session.add(user)
            db.session.commit()
            click.echo(f"Created user with email '{email}' and password '{password}'")
            if admin:
                click.echo("This user has admin privileges.")

def create_app(config_name=None):
    """Create and configure the Flask application."""
    # Templates live in app/templates; static assets in project-root 'static/'
    app = Flask(__name__, static_folder='../static')
    
    # Load configuration class
    cfg_name = config_name or os.getenv('FLASK_CONFIG') or ('production' if os.getenv('FLASK_ENV') == 'production' else 'default')
    cfg_class = config.get(cfg_name, config['default'])
    app.config.from_object(cfg_class)
    # Run any config-specific initialization
    if hasattr(cfg_class, 'init_app'):
        cfg_class.init_app(app)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    # Register CLI commands
    register_cli(app)
    
    # Register blueprints (guide style: bp objects)
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Error handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Shell context (minimal)
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Role
        return {'db': db, 'User': User, 'Role': Role}
    
    # Global template context
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}
    
    # Ensure minimal schema columns exist at runtime (dev safety for SQLite)
    try:
        from sqlalchemy import text
        with app.app_context():
            cols = [row['name'] for row in db.session.execute(text("PRAGMA table_info('groups')")).mappings().all()]
            if 'created_at' not in cols:
                db.session.execute(text("ALTER TABLE groups ADD COLUMN created_at DATETIME"))
                db.session.execute(text("UPDATE groups SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
                db.session.commit()
            if 'max_size' not in cols:
                db.session.execute(text("ALTER TABLE groups ADD COLUMN max_size INTEGER DEFAULT 8"))
                db.session.execute(text("UPDATE groups SET max_size = 8 WHERE max_size IS NULL"))
                db.session.commit()
    except Exception:
        # Avoid using db.session outside of an application context here
        # The error will be handled by normal Flask error handlers if it occurs later
        pass

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
