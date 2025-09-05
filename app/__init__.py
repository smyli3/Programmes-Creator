import os
from flask import Flask, render_template
import click
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
bootstrap = Bootstrap()
mail = Mail()
csrf = CSRFProtect()

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

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
               template_folder='../templates',
               static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    # Register CLI commands
    register_cli(app)
    
    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
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
    
    # Make programs available to all templates
    @app.context_processor
    def inject_programs():
        from .models import Program
        return dict(programs=Program.query.all())
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Role
        return {
            'db': db,
            'User': User,
            'Role': Role,
            'Program': Program,
            'create_db': create_db,
            'drop_db': drop_db
        }
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
