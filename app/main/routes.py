from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, current_app, Response
from flask_login import login_required, current_user
from app.main import bp
from .. import db
from ..models import Student, Group, Program, Movement, Membership, WeeklyGroupName, WeeklyInstructorAssignment, User
from ..snowsports_manager import SnowsportsManager
import os
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from uuid import uuid4
import json

# Initialize the manager
manager = SnowsportsManager()

@bp.route('/')
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
        # Render standard error template
        return render_template('errors/500.html'), 500

@bp.route('/healthz')
def healthz():
    """Simple health check endpoint."""
    return Response('ok', mimetype='text/plain', status=200)

@bp.route('/programs')
@login_required
def programs():
    """Placeholder programs page to avoid 404s during testing."""
    try:
        programs = Program.query.order_by(Program.name).all()
    except Exception:
        programs = []
    return render_template('programs.html', programs=programs)

@bp.route('/students')
@login_required
def students():
    """Display all students with filtering and search capabilities."""
    try:
        # Get all students (membership relationship is dynamic; avoid eager loading)
        students = Student.query.order_by(Student.name).all()
        
        # Get unique ability levels for filter dropdown
        abilities = db.session.query(Student.ability_level).distinct().filter(
            Student.ability_level.isnot(None)
        ).order_by(Student.ability_level).all()
        abilities = [a[0] for a in abilities if a[0]]
        
        # Get all groups for filter dropdown
        groups = Group.query.order_by(Group.name).all()
        
        return render_template(
            'students.html',
            students=students,
            abilities=abilities,
            groups=groups,
            now=datetime.utcnow()
        )
    except Exception as e:
        current_app.logger.error(f"Error loading students: {str(e)}")
        flash('Error loading student data', 'error')
        return render_template('students.html', students=[], abilities=[], groups=[])

@bp.route('/groups')
@login_required
def groups_page():
    """Groups page filtered by selected program."""
    program_id = request.args.get('program_id')
    program = None
    groups = []
    try:
        if program_id:
            program = Program.query.get(program_id)
            if program:
                groups = Group.query.filter_by(program_id=program_id).order_by(Group.name).all()
        else:
            # fallback: show recent groups if no program selected
            groups = Group.query.order_by(Group.name).limit(100).all()
    except Exception:
        groups = []
    return render_template('groups.html', groups=groups, program=program)

@bp.route('/programs/<program_id>/groups')
@bp.route('/programs/<program_id>/groups/week/<int:week_number>')
@login_required
def groups_weekly_view(program_id, week_number=None):
    """Enhanced groups view with weekly functionality."""
    program = Program.query.get_or_404(program_id)

    # Default to current week if not specified
    if week_number is None:
        week_number = program.current_week or 1

    # Validate week number
    if week_number < 1 or week_number > (program.max_weeks or 6):
        flash(f'Invalid week number. Program has {program.max_weeks or 6} weeks.', 'warning')
        week_number = program.current_week or 1

    # Get all groups for this program
    groups = Group.query.filter_by(program_id=program_id).order_by(Group.name).all()

    # Prepare data for template
    groups_data = []
    for g in groups:
        # Weekly name overlay (fallback to base name)
        weekly_name = None
        try:
            weekly_name = WeeklyGroupName.query.filter_by(group_id=g.id, week_number=week_number).first()
        except Exception:
            weekly_name = None

        # Active members for this week
        members = []
        try:
            members = Membership.query.filter_by(group_id=g.id, week_number=week_number, is_active=True).all()
        except Exception:
            members = []

        # Instructor for this week
        instructor_name = None
        try:
            assignment = WeeklyInstructorAssignment.query.filter_by(group_id=g.id, week_number=week_number).first()
            if assignment and assignment.instructor_id:
                inst = User.query.get(assignment.instructor_id)
                instructor_name = inst.username if inst else None
        except Exception:
            instructor_name = None

        groups_data.append({
            'group': g,
            'weekly_name': weekly_name.name if weekly_name else g.name,
            'members': members,
            'instructor': instructor_name,
        })

    # Unassigned students this week
    assigned_ids_subq = db.session.query(Membership.student_id).filter(
        Membership.week_number == week_number,
        Membership.is_active == True,
        Membership.group_id.in_([gg.id for gg in groups])
    ).subquery()
    unassigned_students = Student.query.filter(
        Student.program_id == program.id,
        ~Student.id.in_(assigned_ids_subq)
    ).order_by(Student.name).all()

    available_weeks = list(range(1, (program.max_weeks or 6) + 1))

    # Instructors list (simple: all users; role filtering can be added if needed)
    try:
        instructors = User.query.all()
    except Exception:
        instructors = []

    return render_template(
        'groups_weekly.html',
        program=program,
        current_week=week_number,
        available_weeks=available_weeks,
        groups_data=groups_data,
        unassigned_students=unassigned_students,
        instructors=instructors,
    )

@bp.route('/api/groups/<group_id>/rename', methods=['PUT'])
@login_required
def rename_group_weekly(group_id):
    data = request.get_json() or {}
    week_number = data.get('week_number', type=int)
    new_name = (data.get('name') or '').strip()
    if not new_name or not week_number:
        return jsonify({'error': 'Invalid payload'}), 400
    group = Group.query.get_or_404(group_id)
    try:
        record = WeeklyGroupName.query.filter_by(group_id=group.id, week_number=week_number).first()
        if record:
            record.name = new_name
        else:
            db.session.add(WeeklyGroupName(group_id=group.id, week_number=week_number, name=new_name))
        db.session.commit()
        return jsonify({'success': True, 'name': new_name})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/groups/<group_id>/assign_instructor', methods=['PUT'])
@login_required
def assign_instructor_weekly(group_id):
    data = request.get_json() or {}
    week_number = data.get('week_number', type=int)
    instructor_id = data.get('instructor_id')
    group = Group.query.get_or_404(group_id)
    try:
        rec = WeeklyInstructorAssignment.query.filter_by(group_id=group.id, week_number=week_number).first()
        if rec:
            rec.instructor_id = instructor_id
            rec.assigned_at = datetime.utcnow()
        else:
            db.session.add(WeeklyInstructorAssignment(group_id=group.id, week_number=week_number, instructor_id=instructor_id))
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/students/<student_id>/move', methods=['PUT'])
@login_required
def move_student_weekly(student_id):
    data = request.get_json() or {}
    week_number = data.get('week_number', type=int)
    new_group_id = data.get('group_id')
    if not (week_number and new_group_id):
        return jsonify({'error': 'Invalid payload'}), 400
    student = Student.query.get_or_404(student_id)
    new_group = Group.query.get_or_404(new_group_id)
    if new_group.program_id != student.program_id:
        return jsonify({'error': 'Group is in a different program'}), 400
    # capacity check
    current_count = Membership.query.filter_by(group_id=new_group.id, week_number=week_number, is_active=True).count()
    if new_group.max_size and current_count >= new_group.max_size:
        return jsonify({'error': 'Group at capacity'}), 400
    try:
        # deactivate existing membership for this week
        existing = Membership.query.filter_by(student_id=student.id, week_number=week_number, is_active=True).first()
        if existing:
            existing.is_active = False
            existing.left_at = datetime.utcnow()
        # add new
        db.session.add(Membership(student_id=student.id, group_id=new_group.id, week_number=week_number, is_active=True, joined_at=datetime.utcnow()))
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/students/bulk_move', methods=['PUT'])
@login_required
def bulk_move_students():
    data = request.get_json() or {}
    student_ids = data.get('student_ids') or []
    week_number = data.get('week_number', type=int)
    new_group_id = data.get('group_id')
    if not student_ids:
        return jsonify({'error': 'No students provided'}), 400
    new_group = Group.query.get_or_404(new_group_id)
    # capacity check
    current_count = Membership.query.filter_by(group_id=new_group.id, week_number=week_number, is_active=True).count()
    if new_group.max_size and current_count + len(student_ids) > new_group.max_size:
        return jsonify({'error': 'Not enough capacity'}), 400
    try:
        moved = 0
        for sid in student_ids:
            student = Student.query.get(sid)
            if not student or student.program_id != new_group.program_id:
                continue
            existing = Membership.query.filter_by(student_id=student.id, week_number=week_number, is_active=True).first()
            if existing:
                existing.is_active = False
                existing.left_at = datetime.utcnow()
            db.session.add(Membership(student_id=student.id, group_id=new_group.id, week_number=week_number, is_active=True, joined_at=datetime.utcnow()))
            moved += 1
        db.session.commit()
        return jsonify({'success': True, 'moved': moved})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/programs/<program_id>/advance_week', methods=['POST'])
@login_required
def advance_program_week(program_id):
    program = Program.query.get_or_404(program_id)
    try:
        max_weeks = program.max_weeks or 6
        if (program.current_week or 1) < max_weeks:
            program.current_week = (program.current_week or 1) + 1
            db.session.commit()
            return jsonify({'success': True, 'current_week': program.current_week})
        return jsonify({'error': 'Already at final week'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/programs/<program_id>/generate_weekly', methods=['POST'])
@login_required
def generate_groups_weekly(program_id):
    """Generate groups for a specific week using weekly logic (ability-normalized, balanced)."""
    program = Program.query.get_or_404(program_id)
    week = request.form.get('week_number', type=int) or program.current_week or 1
    max_size = request.form.get('max_size', type=int) or 8
    try:
        created = manager.create_groups_weekly(program_id, week_number=week, max_group_size=max_size)
        flash(f'Generated {created} groups for week {week}.', 'success')
    except Exception as e:
        current_app.logger.exception('Error generating weekly groups')
        flash(f'Error generating groups: {str(e)}', 'danger')
    return redirect(url_for('main.groups_weekly_view', program_id=program_id, week_number=week))

@bp.route('/programs/<program_id>/generate_groups', methods=['POST'])
@login_required
def generate_groups(program_id):
    """Generate groups for a program using basic ability/age rules."""
    max_size = request.form.get('max_size', type=int) or 6
    keep_existing = bool(request.form.get('keep_existing'))
    success, message = manager.create_groups(program_id, max_group_size=max_size, keep_existing=keep_existing)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('main.groups_page', program_id=program_id))

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """Handle file uploads for student data."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        program_id = request.form.get('program_id')
        new_program_name = request.form.get('program_name', '').strip()
        duplicate_strategy = request.form.get('duplicate_strategy', 'skip')
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.instance_path, 'uploads'))
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # If no program selected, create a new one if a name is provided
            if not program_id and new_program_name:
                program = Program(id=str(uuid4()), name=new_program_name, active=True)
                db.session.add(program)
                db.session.commit()
                program_id = program.id
                flash(f"Created program '{program.name}'.", 'success')

            # If still no program, abort and ask user
            if not program_id:
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash('Please select an existing program or enter a new program name.', 'warning')
                return redirect(url_for('main.upload_file'))

            success, message = manager.process_file(filepath, program_id, duplicate_strategy=duplicate_strategy)
            flash(message)
            
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
            return redirect(url_for('main.index'))
    
    # GET: render upload page with existing programs
    try:
        programs = Program.query.order_by(Program.name).all()
    except Exception:
        programs = []
    return render_template('upload.html', programs=programs)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

# Add more routes as needed
