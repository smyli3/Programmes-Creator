from flask import Flask, jsonify
from flask_cors import CORS
import os

def create_app():
    """Application factory function to create and configure the Flask app."""
    # Create the Flask application with template folder
    app = Flask(
        __name__,
        template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
        static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    )
    
    CORS(app)  # Enable CORS for all routes
    
    # Configuration
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from .routes.program_routes import program_bp
    app.register_blueprint(program_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found', 'message': str(error)}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
    
    return app
