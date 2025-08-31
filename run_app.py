import os
import sys
from flask import Flask, render_template

# Set up the application
app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))

# Simple test route
@app.route('/')
def test():
    return "Hello, World! If you see this, the app is running."

# Route to test template loading
@app.route('/test_template')
def test_template():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}"

if __name__ == '__main__':
    print(f"Current working directory: {os.getcwd()}")
    print(f"Template folder: {app.template_folder}")
    print(f"Index.html exists: {os.path.exists(os.path.join(app.template_folder, 'index.html'))}")
    
    # Run the app
    app.run(debug=True, port=5000)
