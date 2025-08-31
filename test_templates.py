import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask

# Create a test app
test_app = Flask(
    __name__,
    template_folder=os.path.join(project_root, 'templates'),
    static_folder=os.path.join(project_root, 'static')
)

# Print debug information
print(f"Project root: {project_root}")
print(f"Template folder: {test_app.template_folder}")
print(f"Static folder: {test_app.static_folder}")

# Check if index.html exists
index_path = os.path.join(test_app.template_folder, 'index.html')
print(f"\nLooking for index.html at: {index_path}")
print(f"index.html exists: {os.path.exists(index_path)}")

# List all files in templates directory
print("\nFiles in templates directory:")
try:
    for file in os.listdir(test_app.template_folder):
        print(f"- {file}")
except Exception as e:
    print(f"Error listing templates directory: {e}")

# Test template loading
try:
    with test_app.app_context():
        template = test_app.jinja_env.get_template('index.html')
        print("\nSuccessfully loaded index.html template!")
except Exception as e:
    print(f"\nError loading template: {e}")
    print("\nCurrent working directory:", os.getcwd())
    print("Python path:", sys.path)
