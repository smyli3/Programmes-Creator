import os
import sys
import webbrowser
import threading
import time
from src import create_app

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def open_browser():
    """Open the default web browser to the app's URL."""
    # Give the server a moment to start
    time.sleep(1.5)
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    try:
        # Create the application with explicit template and static paths
        app = create_app()
        
        # Print debug information
        print(f"Current working directory: {os.getcwd()}")
        print(f"Template folder: {app.template_folder}")
        print(f"Static folder: {app.static_folder}")
        
        # Ensure the upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        
        # Verify templates exist
        index_path = os.path.join(app.template_folder, 'index.html')
        print(f"Looking for index.html at: {index_path}")
        print(f"Index.html exists: {os.path.exists(index_path)}")
        
        # Start the browser in a separate thread
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        print("\nStarting Flask development server...")
        print(" * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)")
        
        # Run the application
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid double execution
        )
        
    except Exception as e:
        print(f"\nError starting application: {str(e)}", file=sys.stderr)
        if 'app' in locals():
            print(f"Template folder: {app.template_folder}")
            print(f"Static folder: {app.static_folder}")
        sys.exit(1)
