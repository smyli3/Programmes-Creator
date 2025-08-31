from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from .. import db
from ..models import Student, Group, Program, Movement
from ..snowsports_manager import SnowsportsManager
import os
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import json

# Initialize the manager
manager = SnowsportsManager()

@main.route('/')
def index():
    """Home page with program overview."""
    programs = Program.query.all()
    return render_template('index.html', programs=programs)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """Handle file uploads for student data."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        program_id = request.form.get('program_id')
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            success, message = manager.process_file(filepath, program_id)
            flash(message)
            
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
            return redirect(url_for('main.index'))
    
    return render_template('upload.html')

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

# Add more routes as needed
