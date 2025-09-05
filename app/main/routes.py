from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import Student, Group, Program, Movement, Membership
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
    try:
        from ..models import Program, Group, Student, Membership
        
        programs = Program.query.filter_by(active=True).order_by(Program.name).all()
        groups = {}
        students = {}
        program = None
        no_programs = len(programs) == 0
        
        # If there are programs, get the first one by default
        if programs:
            program = programs[0]
            
            # Get all groups for the program with student counts
            groups = {}
            for group in program.groups.all():
                # Get active memberships for this group
                student_count = Membership.query.filter_by(
                    group_id=group.id, 
                    is_active=True
                ).count()
                
                groups[str(group.id)] = {
                    'id': group.id,
                    'name': group.name,
                    'instructor': group.instructor if hasattr(group, 'instructor') else None,
                    'notes': group.notes if hasattr(group, 'notes') else None,
                    'student_count': student_count
                }
            
            # Get all students in the program with their group assignments
            students = {}
            for student in program.students.all():
                # Get active membership for this student
                membership = Membership.query.filter_by(
                    student_id=student.id,
                    is_active=True
                ).first()
                
                students[str(student.id)] = {
                    'id': student.id,
                    'name': student.name,
                    'ability_level': student.ability_level,
                    'group_id': str(membership.group_id) if membership else None
                }
        
        return render_template(
            'index.html',
            programs=programs,
            program=program,
            groups=groups,
            students=students,
            no_programs=no_programs
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in index route: {str(e)}", exc_info=True)
        # Return a minimal template with just the error message
        return render_template('error.html', error=str(e)), 500

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
