# Weekly Student Movement System - Complete Implementation

## Database Schema Changes

### Migration Script (create via `flask db migrate`)

```python
"""Add weekly tracking to groups and memberships

Revision ID: add_weekly_tracking
Revises: previous_revision
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

def upgrade():
    # Add week_number to memberships for historical tracking
    op.add_column('memberships', sa.Column('week_number', sa.Integer(), nullable=True))
    
    # Add max_weeks to programs
    op.add_column('programs', sa.Column('max_weeks', sa.Integer(), nullable=False, server_default='6'))
    
    # Add current_week to programs
    op.add_column('programs', sa.Column('current_week', sa.Integer(), nullable=False, server_default='1'))
    
    # Add max_size to groups if not exists
    try:
        op.add_column('groups', sa.Column('max_size', sa.Integer(), nullable=False, server_default='8'))
    except:
        pass  # Column might already exist
    
    # Create weekly_group_names table for week-specific group names
    op.create_table('weekly_group_names',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'week_number')
    )
    
    # Create weekly_instructor_assignments table
    op.create_table('weekly_instructor_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'week_number')
    )
    
    # Add indexes for performance
    op.create_index('ix_memberships_week_active', 'memberships', ['week_number', 'is_active'])
    op.create_index('ix_weekly_group_names_lookup', 'weekly_group_names', ['group_id', 'week_number'])
    op.create_index('ix_weekly_instructor_assignments_lookup', 'weekly_instructor_assignments', ['group_id', 'week_number'])

def downgrade():
    op.drop_index('ix_weekly_instructor_assignments_lookup')
    op.drop_index('ix_weekly_group_names_lookup')
    op.drop_index('ix_memberships_week_active')
    
    op.drop_table('weekly_instructor_assignments')
    op.drop_table('weekly_group_names')
    
    op.drop_column('groups', 'max_size')
    op.drop_column('programs', 'current_week')
    op.drop_column('programs', 'max_weeks')
    op.drop_column('memberships', 'week_number')
```

## Updated Models (`app/models.py`)

```python
from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import and_, or_

class Program(db.Model):
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    max_weeks = db.Column(db.Integer, nullable=False, default=6)
    current_week = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='program', lazy=True, cascade='all, delete-orphan')
    groups = db.relationship('Group', backref='program', lazy=True, cascade='all, delete-orphan')
    
    def get_week_range(self):
        """Return list of available weeks [1, 2, 3, ..., max_weeks]"""
        return list(range(1, self.max_weeks + 1))
    
    def advance_week(self):
        """Move program to next week"""
        if self.current_week < self.max_weeks:
            self.current_week += 1
            db.session.commit()
            return True
        return False

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Base name
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    ability_level = db.Column(db.String(50))
    max_size = db.Column(db.Integer, nullable=False, default=8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='group', lazy=True, cascade='all, delete-orphan')
    weekly_names = db.relationship('WeeklyGroupName', backref='group', lazy=True, cascade='all, delete-orphan')
    instructor_assignments = db.relationship('WeeklyInstructorAssignment', backref='group', lazy=True, cascade='all, delete-orphan')
    
    def get_name_for_week(self, week_number):
        """Get group name for specific week, fallback to base name"""
        weekly_name = WeeklyGroupName.query.filter_by(
            group_id=self.id, 
            week_number=week_number
        ).first()
        return weekly_name.name if weekly_name else self.name
    
    def set_name_for_week(self, week_number, name):
        """Set group name for specific week"""
        weekly_name = WeeklyGroupName.query.filter_by(
            group_id=self.id, 
            week_number=week_number
        ).first()
        
        if weekly_name:
            weekly_name.name = name
        else:
            weekly_name = WeeklyGroupName(
                group_id=self.id,
                week_number=week_number,
                name=name
            )
            db.session.add(weekly_name)
    
    def get_instructor_for_week(self, week_number):
        """Get instructor for specific week"""
        assignment = WeeklyInstructorAssignment.query.filter_by(
            group_id=self.id,
            week_number=week_number
        ).first()
        return assignment.instructor if assignment else None
    
    def set_instructor_for_week(self, week_number, instructor_id):
        """Set instructor for specific week"""
        assignment = WeeklyInstructorAssignment.query.filter_by(
            group_id=self.id,
            week_number=week_number
        ).first()
        
        if assignment:
            assignment.instructor_id = instructor_id
            assignment.assigned_at = datetime.utcnow()
        else:
            assignment = WeeklyInstructorAssignment(
                group_id=self.id,
                week_number=week_number,
                instructor_id=instructor_id
            )
            db.session.add(assignment)
    
    def get_students_for_week(self, week_number):
        """Get active students for specific week"""
        return Student.query.join(Membership).filter(
            and_(
                Membership.group_id == self.id,
                Membership.week_number == week_number,
                Membership.is_active == True
            )
        ).all()
    
    def get_capacity_for_week(self, week_number):
        """Get current/max capacity for specific week"""
        current_count = Membership.query.filter(
            and_(
                Membership.group_id == self.id,
                Membership.week_number == week_number,
                Membership.is_active == True
            )
        ).count()
        return f"{current_count}/{self.max_size}"

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    ability_level = db.Column(db.String(50))
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='student', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='student', lazy=True, cascade='all, delete-orphan')
    
    @property
    def age(self):
        """Calculate current age from birth_date"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    def get_group_for_week(self, week_number):
        """Get current group for specific week"""
        membership = Membership.query.filter(
            and_(
                Membership.student_id == self.id,
                Membership.week_number == week_number,
                Membership.is_active == True
            )
        ).first()
        return membership.group if membership else None
    
    def move_to_group_for_week(self, week_number, new_group_id):
        """Move student to different group for specific week"""
        # Deactivate current membership for this week
        current_membership = Membership.query.filter(
            and_(
                Membership.student_id == self.id,
                Membership.week_number == week_number,
                Membership.is_active == True
            )
        ).first()
        
        if current_membership:
            current_membership.is_active = False
            current_membership.left_at = datetime.utcnow()
        
        # Create new membership
        new_membership = Membership(
            student_id=self.id,
            group_id=new_group_id,
            week_number=week_number,
            is_active=True,
            joined_at=datetime.utcnow()
        )
        db.session.add(new_membership)
        
    def get_weekly_history(self):
        """Get student's group history across all weeks"""
        memberships = Membership.query.filter_by(
            student_id=self.id
        ).order_by(Membership.week_number, Membership.joined_at).all()
        
        history = {}
        for membership in memberships:
            if membership.is_active:
                history[membership.week_number] = {
                    'group': membership.group,
                    'joined_at': membership.joined_at
                }
        return history

class Membership(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    __table_args__ = (
        db.Index('ix_memberships_week_active', 'week_number', 'is_active'),
    )

class WeeklyGroupName(db.Model):
    __tablename__ = 'weekly_group_names'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('group_id', 'week_number'),
        db.Index('ix_weekly_group_names_lookup', 'group_id', 'week_number'),
    )

class WeeklyInstructorAssignment(db.Model):
    __tablename__ = 'weekly_instructor_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    instructor = db.relationship('User', backref='instructor_assignments')
    
    __table_args__ = (
        db.UniqueConstraint('group_id', 'week_number'),
        db.Index('ix_weekly_instructor_assignments_lookup', 'group_id', 'week_number'),
    )

# Existing models (User, Note) remain unchanged
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'admin', 'instructor', 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)
    
    # Relationships
    author = db.relationship('User', backref='notes_authored')
```

## Updated Routes (`app/main/routes.py`)

```python
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.main import bp
from app.models import Program, Group, Student, Membership, WeeklyGroupName, WeeklyInstructorAssignment, User
from app import db
from datetime import datetime
import json

@bp.route('/programs/<int:program_id>/groups')
@bp.route('/programs/<int:program_id>/groups/week/<int:week_number>')
@login_required
def groups_weekly_view(program_id, week_number=None):
    """Enhanced groups view with weekly functionality"""
    program = Program.query.get_or_404(program_id)
    
    # Default to current week if not specified
    if week_number is None:
        week_number = program.current_week
    
    # Validate week number
    if week_number < 1 or week_number > program.max_weeks:
        flash(f'Invalid week number. Program has {program.max_weeks} weeks.', 'error')
        week_number = program.current_week
    
    # Get all groups for this program
    groups = Group.query.filter_by(program_id=program_id).all()
    
    # Get instructors (users with instructor role)
    instructors = User.query.filter_by(role='instructor').all()
    
    # Prepare group data with weekly information
    groups_data = []
    for group in groups:
        students = group.get_students_for_week(week_number)
        groups_data.append({
            'group': group,
            'weekly_name': group.get_name_for_week(week_number),
            'students': students,
            'capacity': group.get_capacity_for_week(week_number),
            'instructor': group.get_instructor_for_week(week_number)
        })
    
    # Get unassigned students for this week
    assigned_student_ids = db.session.query(Membership.student_id).filter(
        db.and_(
            Membership.week_number == week_number,
            Membership.is_active == True,
            Membership.group_id.in_([g.id for g in groups])
        )
    ).subquery()
    
    unassigned_students = Student.query.filter(
        db.and_(
            Student.program_id == program_id,
            ~Student.id.in_(assigned_student_ids)
        )
    ).all()
    
    return render_template('groups_weekly.html',
                         program=program,
                         current_week=week_number,
                         available_weeks=program.get_week_range(),
                         groups_data=groups_data,
                         unassigned_students=unassigned_students,
                         instructors=instructors)

@bp.route('/api/groups/<int:group_id>/rename', methods=['PUT'])
@login_required
def rename_group_weekly(group_id):
    """Rename group for specific week"""
    data = request.get_json()
    week_number = data.get('week_number')
    new_name = data.get('name', '').strip()
    
    if not new_name:
        return jsonify({'error': 'Name cannot be empty'}), 400
    
    group = Group.query.get_or_404(group_id)
    
    try:
        group.set_name_for_week(week_number, new_name)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Group renamed to "{new_name}" for week {week_number}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/groups/<int:group_id>/assign_instructor', methods=['PUT'])
@login_required
def assign_instructor_weekly(group_id):
    """Assign instructor to group for specific week"""
    data = request.get_json()
    week_number = data.get('week_number')
    instructor_id = data.get('instructor_id')
    
    group = Group.query.get_or_404(group_id)
    
    # Validate instructor exists
    if instructor_id:
        instructor = User.query.get(instructor_id)
        if not instructor or instructor.role != 'instructor':
            return jsonify({'error': 'Invalid instructor'}), 400
    
    try:
        group.set_instructor_for_week(week_number, instructor_id)
        db.session.commit()
        
        instructor_name = instructor.username if instructor_id else 'None'
        return jsonify({
            'success': True,
            'message': f'Instructor set to {instructor_name} for week {week_number}',
            'instructor_name': instructor_name
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/students/<int:student_id>/move', methods=['PUT'])
@login_required
def move_student_weekly(student_id):
    """Move student to different group for specific week"""
    data = request.get_json()
    week_number = data.get('week_number')
    new_group_id = data.get('group_id')
    
    student = Student.query.get_or_404(student_id)
    new_group = Group.query.get_or_404(new_group_id)
    
    # Validate group belongs to same program
    if new_group.program_id != student.program_id:
        return jsonify({'error': 'Cannot move student to group in different program'}), 400
    
    # Check group capacity
    current_capacity = len(new_group.get_students_for_week(week_number))
    if current_capacity >= new_group.max_size:
        return jsonify({'error': 'Group is at maximum capacity'}), 400
    
    try:
        student.move_to_group_for_week(week_number, new_group_id)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{student.name} moved to {new_group.get_name_for_week(week_number)} for week {week_number}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/students/bulk_move', methods=['PUT'])
@login_required
def bulk_move_students():
    """Move multiple students to a group for specific week"""
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    week_number = data.get('week_number')
    new_group_id = data.get('group_id')
    
    if not student_ids:
        return jsonify({'error': 'No students selected'}), 400
    
    new_group = Group.query.get_or_404(new_group_id)
    students = Student.query.filter(Student.id.in_(student_ids)).all()
    
    # Validate capacity
    current_capacity = len(new_group.get_students_for_week(week_number))
    if current_capacity + len(students) > new_group.max_size:
        return jsonify({'error': 'Not enough space in target group'}), 400
    
    try:
        moved_count = 0
        for student in students:
            if student.program_id == new_group.program_id:
                student.move_to_group_for_week(week_number, new_group_id)
                moved_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{moved_count} students moved to {new_group.get_name_for_week(week_number)}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/programs/<int:program_id>/advance_week', methods=['POST'])
@login_required
def advance_program_week(program_id):
    """Advance program to next week"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Only admins can advance weeks'}), 403
    
    program = Program.query.get_or_404(program_id)
    
    if program.advance_week():
        return jsonify({
            'success': True,
            'message': f'Program advanced to week {program.current_week}',
            'current_week': program.current_week
        })
    else:
        return jsonify({'error': 'Program is already at final week'}), 400

@bp.route('/api/students/<int:student_id>/history')
@login_required
def student_weekly_history(student_id):
    """Get student's group history across weeks"""
    student = Student.query.get_or_404(student_id)
    history = student.get_weekly_history()
    
    # Format for JSON response
    formatted_history = {}
    for week, data in history.items():
        formatted_history[str(week)] = {
            'group_name': data['group'].get_name_for_week(week),
            'group_id': data['group'].id,
            'joined_at': data['joined_at'].isoformat()
        }
    
    return jsonify({
        'student_name': student.name,
        'history': formatted_history
    })

# Updated SnowsportsManager to handle weekly memberships
@bp.route('/programs/<int:program_id>/generate_groups', methods=['POST'])
@login_required
def generate_groups_weekly(program_id):
    """Generate initial groups for week 1"""
    program = Program.query.get_or_404(program_id)
    week_number = 1  # Always generate for week 1 initially
    
    # Get form data
    max_group_size = request.form.get('max_group_size', 8, type=int)
    
    try:
        from app.snowsports_manager import SnowsportsManager
        manager = SnowsportsManager()
        
        # Generate groups with weekly memberships
        groups_created = manager.create_groups_weekly(program_id, week_number, max_group_size)
        
        flash(f'Generated {groups_created} groups for {program.name} week {week_number}', 'success')
        return redirect(url_for('main.groups_weekly_view', program_id=program_id, week_number=week_number))
        
    except Exception as e:
        flash(f'Error generating groups: {str(e)}', 'error')
        return redirect(url_for('main.program_detail', id=program_id))
```

## Updated SnowsportsManager (`app/snowsports_manager.py`)

```python
from app.models import Student, Group, Membership, Program
from app import db
from datetime import datetime
import math

class SnowsportsManager:
    
    def create_groups_weekly(self, program_id, week_number, max_group_size=8):
        """Create groups for specific week with weekly memberships"""
        program = Program.query.get_or_404(program_id)
        students = Student.query.filter_by(program_id=program_id).all()
        
        if not students:
            raise ValueError("No students found in program")
        
        # Clear existing memberships for this week
        Membership.query.filter(
            db.and_(
                Membership.group_id.in_(
                    db.session.query(Group.id).filter_by(program_id=program_id)
                ),
                Membership.week_number == week_number
            )
        ).delete(synchronize_session=False)
        
        # Clear existing groups if this is week 1
        if week_number == 1:
            Group.query.filter_by(program_id=program_id).delete()
        
        # Group students by ability level
        ability_groups = {}
        for student in students:
            ability = student.ability_level or 'Unknown'
            if ability not in ability_groups:
                ability_groups[ability] = []
            ability_groups[ability].append(student)
        
        groups_created = 0
        
        for ability_level, ability_students in ability_groups.items():
            # Sort by age within ability level
            ability_students.sort(key=lambda s: s.age or 0)
            
            # Calculate number of groups needed
            num_groups = math.ceil(len(ability_students) / max_group_size)
            
            # Create groups for this ability level
            for i in range(num_groups):
                # Create group (only if week 1, otherwise reuse existing)
                if week_number == 1:
                    group = Group(
                        name=f"{ability_level} Group {i + 1}",
                        program_id=program_id,
                        ability_level=ability_level,
                        max_size=max_group_size
                    )
                    db.session.add(group)
                    db.session.flush()  # Get group ID
                    groups_created += 1
                else:
                    # Find existing group for this ability/index
                    group = Group.query.filter_by(
                        program_id=program_id,
                        ability_level=ability_level
                    ).offset(i).first()
                    
                    if not group:
                        # Create new group if needed
                        group = Group(
                            name=f"{ability_level} Group {i + 1}",
                            program_id=program_id,
                            ability_level=ability_level,
                            max_size=max_group_size
                        )
                        db.session.add(group)
                        db.session.flush()
                        groups_created += 1
                
                # Assign students to this group for this week
                start_idx = i * max_group_size
                end_idx = min(start_idx + max_group_size, len(ability_students))
                
                for j in range(start_idx, end_idx):
                    student = ability_students[j]
                    
                    membership = Membership(
                        student_id=student.id,
                        group_id=group.id,
                        week_number=week_number,
                        is_active=True,
                        joined_at=datetime.utcnow()
                    )
                    db.session.add(membership)
        
        db.session.commit()
        return groups_created
    
    def copy_week_structure(self, program_id, from_week, to_week):
        """Copy group structure from one week to another"""
        program = Program.query.get_or_404(program_id)
        
        # Validate weeks
        if from_week < 1 or from_week > program.max_weeks:
            raise ValueError(f"Invalid from_week: {from_week}")
        if to_week < 1 or to_week > program.max_weeks:
            raise ValueError(f"Invalid to_week: {to_week}")
        
        # Get all active memberships from source week
        source_memberships = Membership.query.filter(
            db.and_(
                Membership.week_number == from_week,
                Membership.is_active == True,
                Membership.group_id.in_(
                    db.session.query(Group.id).filter_by(program_id=program_id)
                )
            )
        ).all()
        
        # Clear existing memberships for target week
        Membership.query.filter(
            db.and_(
                Membership.week_number == to_week,
                Membership.group_id.in_(
                