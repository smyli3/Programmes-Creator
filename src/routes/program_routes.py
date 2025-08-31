from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import io

from src.models.models import db, Student, Group, Membership, Movement, Progress
from src.services.grouping import build_stage1, build_stage2, pack_excel

program_bp = Blueprint('program', __name__)

# Ensure upload folder exists
def init_upload_folder():
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

@program_bp.route('/')
def index():
    """Render the main page with upload form."""
    return render_template('index.html')

@program_bp.route('/upload', methods=['POST'])
def upload():
    """Handle file upload and process stage 1 grouping."""
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    if file and file.filename.endswith(('.csv', '.xlsx')):
        try:
            # Read the uploaded file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Process stage 1 grouping
            group_size = int(request.form.get('group_size', 6))
            summary_df, instructor_assign_df, profiles_df, stage1_groups_df, program_start_date = build_stage1(df, group_size)
            
            # Save to database (in a real app, you'd use a transaction)
            db.session.begin()
            try:
                # Clear existing data
                db.session.query(Membership).delete()
                db.session.query(Student).delete()
                db.session.query(Group).delete()
                
                # Save groups
                groups = {}
                for _, row in summary_df.iterrows():
                    group = Group(
                        code=row['ProposedGroupID'],
                        ability=row['Ability']
                    )
                    db.session.add(group)
                    groups[row['ProposedGroupID']] = group
                
                # Save students and memberships
                for _, row in stage1_groups_df.iterrows():
                    student = Student(
                        customer_id=row['CustomerID'],
                        name=row['CustomerName'],
                        ability_start=row['Ability'],
                        parent_name=row.get('ParentName', ''),
                        email=row.get('Email', ''),
                        emergency_phone=row.get('EmergencyPhone', '')
                    )
                    db.session.add(student)
                    
                    # Create membership for week 1
                    membership = Membership(
                        student=student,
                        group=groups[row['ProposedGroupID']],
                        week=1
                    )
                    db.session.add(membership)
                
                db.session.commit()
                
                # Get the current week number (1-6)
                current_week = (datetime.now().isocalendar()[1] - 1) % 6 + 1
                
                # Get all groups with their students
                groups_data = []
                for group in Group.query.all():
                    students_in_group = [{
                        'id': m.student.id,
                        'customer_id': m.student.customer_id,
                        'name': m.student.name,
                        'ability': m.student.ability_start
                    } for m in group.memberships if m.week == current_week]
                    
                    groups_data.append({
                        'id': group.id,
                        'code': group.code,
                        'ability': group.ability,
                        'instructor': group.instructor or '',
                        'students': students_in_group
                    })
                
                # Get all students not in a group for the current week
                    
                return render_template('groups.html', 
                                    groups=groups_data,
                                    current_week=current_week)
            
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error processing file: {str(e)}")
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(url_for('program.index'))
        
        except Exception as e:
            current_app.logger.error(f"Error reading file: {str(e)}")
            flash(f'Error reading file: {str(e)}', 'error')
            return redirect(url_for('program.index'))
    
    flash('Invalid file type. Please upload a CSV or Excel file.', 'error')
    return redirect(url_for('program.index'))
