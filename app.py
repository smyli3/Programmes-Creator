from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

# We'll use Flask-Login's @login_required decorator instead of our own
import pandas as pd
from datetime import datetime
import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple user model
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

# This would typically be a database lookup
users = {'1': {'username': 'admin', 'password': generate_password_hash('admin')}}

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # In a real app, validate against database
        user_id = None
        for uid, user in users.items():
            if user['username'] == username and check_password_hash(user['password'], password):
                user_id = uid
                break
                
        if user_id:
            user = User(user_id)
            login_user(user)
            return redirect(url_for('index'))
            
        flash('Invalid username or password')
        
    return '''
        <form method="post">
            <p><input type=text name=username placeholder="Username">
            <p><input type=password name=password placeholder="Password">
            <p><input type=submit value=Login>
        </form>
    '''

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@dataclass
class Student:
    """Represents a student in the snowsports program."""
    customer_id: str
    name: str
    age: int
    ability_level: str
    birth_date: str
    parent_name: str = ""
    contact_email: str = ""
    emergency_contact: str = ""
    emergency_phone: str = ""
    food_allergy: str = ""
    medication: str = ""
    special_condition: str = ""
    notes: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert student object to dictionary for JSON serialization."""
        return asdict(self)

@dataclass
class Group:
    """Represents a group of students with an instructor."""
    group_id: str
    name: str
    program_id: str  # Reference to the parent program
    instructor: str = ""
    notes: str = ""
    student_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert group object to dictionary for JSON serialization."""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'program_id': self.program_id,
            'instructor': self.instructor,
            'notes': self.notes,
            'student_ids': self.student_ids,
            'student_count': len(self.student_ids)
        }

@dataclass
class Program:
    """Represents a snowsports program with its own students and groups."""
    program_id: str
    name: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    active: bool = True
    students: Dict[str, Student] = field(default_factory=dict)
    groups: Dict[str, Group] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert program object to dictionary for JSON serialization."""
        return {
            'program_id': self.program_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'active': self.active,
            'student_count': len(self.students),
            'group_count': len(self.groups)
        }

class SnowsportsManager:
    """Manages multiple snowsports programs with their students and groups."""
    
    def _init_default_program(self):
        """Initialize with a default program if none exists."""
        if not self.programs:
            default_program = Program(
                program_id="default",
                name="Default Program",
                description="Automatically created default program"
            )
            self.programs[default_program.program_id] = default_program
    
    def __init__(self):
        self.programs: Dict[str, Program] = {}
        self.column_mapping = {
            'Textbox20': 'program_name',
            'Textbox71': 'relationship_to_student',
            'Textbox37': 'contact_email',
            'CustomerID': 'customer_id',
            'CustomerName': 'name',
            'BirthDate': 'birth_date',
            'ParentName': 'parent_name',
            'PrimaryEmergencyContact': 'emergency_contact',
            'PrimaryEmergencyPhone': 'emergency_phone',
            'FoodAllergy': 'food_allergy',
            'Medication': 'medication',
            'SpecialCondition': 'special_condition'
        }
    
    def map_column_names(self, df):
        """Map generic column names to meaningful ones."""
        # Apply the column mapping
        df = df.rename(columns={k: v for k, v in self.column_mapping.items() if k in df.columns})
        return df

    def get_program_name(self, row):
        """Extract program name from the data."""
        if 'ProgramName' in row and pd.notna(row['ProgramName']):
            return row['ProgramName']
        if 'Textbox20' in row and pd.notna(row['Textbox20']):
            return row['Textbox20']
        return "Unknown Program"

    def process_ability_level(self, product_desc):
        """Map product description to ability level."""
        if not isinstance(product_desc, str):
            return "Unknown"
            
        # Extract the level code (e.g., 'FT' from 'Ride Tribe - FT')
        level_match = product_desc.strip().split('-')[-1].strip()
        
        # Map to ability levels
        ability_map = {
            'FT': 'First Time',
            'BZ1': 'Beginner 1',
            'BZ2': 'Beginner 2',
            'NZ': 'Novice',
            'IZ1': 'Blue Intermediate',
            'IZ2': 'Red Intermediate',
            'AZ': 'Advanced'
        }
        
        return ability_map.get(level_match, 'Unknown')

    def get_program(self, program_id: str) -> Optional[Program]:
        """Get a program by ID."""
        return self.programs.get(program_id)
    
    def create_program(self, name: str, description: str = "") -> tuple[bool, str, Optional[Program]]:
        """Create a new program.
        
        Args:
            name: Name of the program
            description: Optional description
            
        Returns:
            Tuple of (success: bool, message: str, program: Optional[Program])
        """
        if not name:
            return False, "Program name cannot be empty", None
            
        # Create a URL-safe ID from the name
        program_id = name.lower().replace(' ', '_')
        
        if program_id in self.programs:
            return False, f"A program with name '{name}' already exists", None
            
        program = Program(
            program_id=program_id,
            name=name,
            description=description
        )
        self.programs[program_id] = program
        return True, f"Program '{name}' created successfully", program
    
    def delete_program(self, program_id: str) -> tuple[bool, str]:
        """Delete a program and all its data.
        
        Args:
            program_id: ID of the program to delete
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if program_id not in self.programs:
            return False, "Program not found"
            
        if len(self.programs) == 1:
            return False, "Cannot delete the last program"
            
        del self.programs[program_id]
        return True, f"Program deleted successfully"
    
    def process_file(self, filepath: str, program_id: str = None) -> tuple[bool, str]:
        """Process the uploaded file and update the student data for a specific program.
        
        Args:
            filepath: Path to the uploaded file (CSV or Excel)
            program_id: ID of the program to add the students to
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not program_id and self.programs:
            program_id = next(iter(self.programs))  # Use first program as default
            
        if program_id not in self.programs:
            return False, f"Program with ID {program_id} not found"
            
        program = self.programs[program_id]
        
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:  # Excel file
                df = pd.read_excel(filepath, engine='openpyxl')
            
            # Map column names
            df = self.map_column_names(df)
            
            # Process each row
            for _, row in df.iterrows():
                # Extract student data from row
                student_data = {
                    'customer_id': row.get('customer_id', ''),
                    'name': row.get('name', ''),
                    'birth_date': row.get('birth_date', ''),
                    'parent_name': row.get('parent_name', ''),
                    'contact_email': row.get('contact_email', ''),
                    'emergency_contact': row.get('emergency_contact', ''),
                    'emergency_phone': row.get('emergency_phone', ''),
                    'food_allergy': row.get('food_allergy', ''),
                    'medication': row.get('medication', ''),
                    'special_condition': row.get('special_condition', '')
                }
                
                # Process ability level
                if 'ProductDescription_1' in row:
                    student_data['ability_level'] = self.process_ability_level(row['ProductDescription_1'])
                
                # Calculate age
                if 'birth_date' in student_data and pd.notna(student_data['birth_date']):
                    try:
                        birth_date = pd.to_datetime(student_data['birth_date'], format='%d-%b-%y')
                        program_start = datetime(2025, 9, 1)
                        student_data['age'] = (program_start - birth_date).days // 365
                    except (ValueError, TypeError):
                        student_data['age'] = 0
                        
                # Create or update student in the program
                student = Student(**student_data)
                program.students[student.customer_id] = student
                
                # Set program name from first student if not set
                if not program.name and 'program_name' in row and pd.notna(row['program_name']):
                    program.name = row['program_name']
                    
            return True, f"Successfully processed {len(df)} students for program '{program.name}'"
            
        except Exception as e:
            return False, str(e)
    
    def create_groups(self, program_id: str, max_group_size: int = 6, keep_existing: bool = False) -> tuple[bool, str]:
        """Create groups of students based on ability level and age for a specific program.
        
        Args:
            program_id: ID of the program to create groups in
            max_group_size: Maximum number of students per group
            keep_existing: Whether to keep existing groups if possible
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if program_id not in self.programs:
            return False, "Program not found"
            
        program = self.programs[program_id]
            
        if not program.students:
            return False, "No student data available."
        
        try:
            # Define ability order for sorting
            ability_order = {
                'First Time': 1,
                'Beginner 1': 2,
                'Beginner 2': 3,
                'Novice': 4,
                'Blue Intermediate': 5,
                'Red Intermediate': 6,
                'Advanced': 7,
                'Unknown': 8
            }
            
            # Get list of students not already in a group
            unassigned_students = [
                student for student in program.students.values()
                if not any(student.customer_id in group.student_ids 
                         for group in program.groups.values())
            ]
            
            if not unassigned_students and not keep_existing:
                return False, "All students are already in groups. Use 'Add Empty Group' instead."
            
            # Clear existing groups if not keeping them
            if not keep_existing:
                program.groups = {}
            
            # Group students by ability level and age
            students_by_ability = {}
            for student in program.students.values():
                key = (student.ability_level, student.age // 2 * 2)  # Group ages in 2-year brackets
                if key not in students_by_ability:
                    students_by_ability[key] = []
                students_by_ability[key].append(student)
            
            # Sort each ability group by name for consistent ordering
            for key in students_by_ability:
                students_by_ability[key].sort(key=lambda s: s.name)
            
            # Create groups
            group_num = 1
            for (ability, _), students in sorted(students_by_ability.items(), 
                                               key=lambda x: (ability_order.get(x[0][0], 9), x[0][1])):
                if len(students) <= max_group_size:
                    group_id = f"{ability[:3].upper()}{group_num}"
                    self._create_group(program_id, group_id, students)
                    group_num += 1
                else:
                    # Split large groups
                    for i in range(0, len(students), max_group_size):
                        group_id = f"{ability[:3].upper()}{group_num}"
                        self._create_group(program_id, group_id, students[i:i + max_group_size])
                        group_num += 1
            
            return True, f"Created {len(program.groups)} groups with {len(program.students)} students in program '{program.name}'."
            
        except Exception as e:
            return False, str(e)

    def _create_group(self, program_id: str, group_id: str, students: List[Student]) -> bool:
        """Create a new group with the given students in the specified program.
        
        Args:
            program_id: ID of the program to create the group in
            group_id: Unique identifier for the group
            students: List of Student objects to add to the group
            
        Returns:
            bool: True if group was created successfully, False otherwise
        """
        if program_id not in self.programs:
            return False
            
        # Create the group if it doesn't exist
        if group_id not in self.programs[program_id].groups:
            self.programs[program_id].groups[group_id] = Group(
                group_id=group_id,
                name=group_id,
                program_id=program_id
            )
            
        # Add students to the group
        group = self.programs[program_id].groups[group_id]
        for student in students:
            if student.customer_id not in group.student_ids:
                group.student_ids.append(student.customer_id)
                
        return True
        
    def _find_student_group(self, program_id: str, student_id: str) -> str:
        """Find which group a student is in.
        
        Args:
            program_id: ID of the program
            student_id: ID of the student
            
        Returns:
            ID of the group the student is in, or 'Ungrouped' if not found
        """
        if program_id not in self.programs:
            return "Ungrouped"
            
        program = self.programs[program_id]
        for group_id, group in program.groups.items():
            if student_id in group.student_ids:
                return group_id
                
        return "Ungrouped"
        
    def add_note(self, program_id: str, student_id: str, note: str, author: str = "System") -> bool:
        """Add a note to a student's record.
        
        Args:
            program_id: ID of the program the student belongs to
            student_id: ID of the student
            note: The note text
            author: Optional author of the note (default: 'System')
            
        Returns:
            bool: True if note was added successfully, False otherwise
        """
        if program_id not in self.programs or student_id not in self.programs[program_id].students:
            return False
            
        student = self.programs[program_id].students[student_id]
        
        if not hasattr(student, 'notes'):
            student.notes = []
            
        student.notes.append({
            'text': note,
            'author': author,
            'timestamp': datetime.now().isoformat()
        })
        return True

manager = SnowsportsManager()

@app.route('/api/programs', methods=['POST'])
@login_required
def api_create_program():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Program name is required'}), 400
        
    name = data['name'].strip()
    description = data.get('description', '').strip()
    
    success, message, program = manager.create_program(name, description)
    if success:
        return jsonify({
            'success': True,
            'message': 'Program created successfully',
            'program': program.to_dict() if program else None
        })
    else:
        return jsonify({'success': False, 'message': message}), 400

@app.route('/api/programs/<program_id>', methods=['DELETE'])
@login_required
def api_delete_program(program_id):
    if not program_id:
        return jsonify({'success': False, 'message': 'Program ID is required'}), 400
        
    success, message = manager.delete_program(program_id)
    if success:
        return jsonify({
            'success': True,
            'message': 'Program deleted successfully'
        })
    else:
        return jsonify({'success': False, 'message': message}), 400

@app.route('/')
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
        
    program_id = request.args.get('program_id')
    
    # If no programs exist, show the new program modal
    if not manager.programs:
        return render_template('index.html', no_programs=True, current_user=current_user)
        
    # If program_id is not provided but programs exist, use the first one
    if not program_id:
        program_id = next(iter(manager.programs.keys()))
        return redirect(url_for('index', program_id=program_id))
    
    program = manager.get_program(program_id)
    if not program:
        # If the requested program doesn't exist, use the first available one
        program_id = next(iter(manager.programs.keys()))
        return redirect(url_for('index', program_id=program_id))
    
    # Get the current week number (1-6)
    current_week = (datetime.now().isocalendar()[1] - 1) % 6 + 1  # Simple week rotation
    
    return render_template(
        'index.html',
        program=program,
        programs=manager.programs.values(),
        students=program.students,
        groups=program.groups,
        current_week=current_week,
        no_programs=False
    )

@app.route('/api/students/<student_id>/notes', methods=['POST'])
@login_required
def add_student_note(student_id):
    program_id = request.args.get('program_id')
    if not program_id:
        return jsonify({'success': False, 'message': 'Program ID is required'}), 400
        
    program = manager.get_program(program_id)
    if not program:
        return jsonify({'success': False, 'message': 'Program not found'}), 404
        
    if student_id not in program.students:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
        
    note = request.json.get('note')
    author = request.json.get('author', 'System')
    
    if not note:
        return jsonify({'success': False, 'message': 'Note text is required'}), 400
        
    success = manager.add_note(program_id, student_id, note, author)
    if success:
        return jsonify({'success': True, 'message': 'Note added'})
    else:
        return jsonify({'success': False, 'message': 'Failed to add note'}), 500
    
    # GET: Return all notes for the student
    notes = manager.get_student_notes(student_id)
    return jsonify({'success': True, 'notes': notes})

@app.route('/api/groups/<group_id>/students/<student_id>', methods=['POST', 'DELETE'])
@login_required
def manage_group_student(group_id, student_id):
    program_id = request.args.get('program_id')
    if not program_id:
        return jsonify({'success': False, 'message': 'Program ID is required'}), 400
        
    program = manager.get_program(program_id)
    if not program:
        return jsonify({'success': False, 'message': 'Program not found'}), 404
        
    if group_id not in program.groups:
        return jsonify({'success': False, 'message': 'Group not found'}), 404
        
    if student_id not in program.students:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
        
    if request.method == 'POST':
        # Add student to group
        if student_id in program.groups[group_id].student_ids:
            return jsonify({'success': False, 'message': 'Student already in group'}), 400
            
        program.groups[group_id].student_ids.append(student_id)
        return jsonify({'success': True, 'message': 'Student added to group'})
        
    elif request.method == 'DELETE':
        # Remove student from group
        if student_id in program.groups[group_id].student_ids:
            program.groups[group_id].student_ids.remove(student_id)
        return jsonify({'success': True, 'message': 'Student removed from group'})

@app.route('/upload/<program_id>', methods=['POST'])
@login_required
def upload_file(program_id):
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'File type not allowed'}), 400
    
    try:
        # Create a secure filename and save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file
        success, message = manager.process_file(filepath, program_id)
        
        # Clean up the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
            
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': f'Error processing file: {message}'}), 400
            
    except Exception as e:
        # Clean up the uploaded file if it exists
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
            
        return jsonify({
            'success': False, 
            'message': f'An error occurred while processing the file: {str(e)}'
        }), 500

@app.route('/create_groups', methods=['POST'])
@login_required
def create_groups():
    program_id = request.form.get('program_id')
    if not program_id:
        return jsonify({'success': False, 'message': 'Program ID is required'}), 400
        
    try:
        max_size = int(request.form.get('max_group_size', 6))
        keep_existing = request.form.get('keep_existing') == 'on'
        
        success, message = manager.create_groups(program_id, max_size, keep_existing)
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
        
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid group size'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/export_checklist')
def export_checklist():
    program_id = request.args.get('program_id')
    if not program_id:
        return "No program ID provided", 400
        
    program = manager.get_program(program_id)
    if not program:
        return "Program not found", 404
    
    # Get current date for the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Check-in List - {program.name} - {current_date}</title>
        <style>
            @page {{
                size: A4;
                margin: 1cm;
            }}
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .header .date {{
                font-size: 16px;
                color: #666;
            }}
            .student-list {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .student-list th, .student-list td {{
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }}
            .student-list th {{
                background-color: #f5f5f5;
                position: sticky;
                top: 0;
            }}
            .student-list tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .check-column {{
                width: 80px;
                text-align: center;
            }}
            .group-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                color: white;
                min-width: 60px;
                text-align: center;
            }}
            @media print {{
                .no-print {{
                    display: none;
                }}
                .student-list th, .student-list td {{
                    border-color: #999;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{program.name}</h1>
            <div class="date">Check-in List - {current_date}</div>
        </div>
        
        <table class="student-list">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Last Name</th>
                    <th>First Name</th>
                    <th>Group</th>
                    <th class="check-column">Present</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Generate group color mapping
    group_colors = {}
    color_palette = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD',
        '#D4A5A5', '#9B786F', '#E8A87C', '#C38D9E', '#85DCB',
        '#E8A87C', '#C38D9E', '#41B3A3', '#E27D60', '#85DCB0'
    ]
    
    for i, group_id in enumerate(program.groups):
        group_colors[group_id] = color_palette[i % len(color_palette)]
    
    # Get all students with their groups
    students = []
    for student in program.students.values():
        group = next((g for g in program.groups.values() if student.id in g.members), None)
        students.append({
            'last_name': student.last_name,
            'first_name': student.first_name,
            'group_id': group.id if group else None,
            'group_name': group.name if group else 'Ungrouped',
            'group_color': group_colors.get(group.id, '#CCCCCC') if group else '#CCCCCC'
        })
    
    # Sort students by last name, then first name
    students.sort(key=lambda x: (x['last_name'].lower(), x['first_name'].lower()))
    
    # Add student rows to HTML
    for i, student in enumerate(students, 1):
        html += f"""
            <tr>
                <td>{i}</td>
                <td>{student['last_name']}</td>
                <td>{student['first_name']}</td>
                <td>
                    <span class="group-badge" style="background-color: {student['group_color']};">
                        {student['group_name']}
                    </span>
                </td>
                <td class="check-column">
                    <input type="checkbox" style="width: 20px; height: 20px;">
                </td>
            </tr>
        """
    
    # Close HTML
    html += """
            </tbody>
        </table>
        
        <div class="no-print" style="margin-top: 30px; text-align: center;">
            <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                Print Checklist
            </button>
        </div>
        
        <script>
            // Add any additional JavaScript if needed
            document.addEventListener('DOMContentLoaded', function() {
                // Auto-print when the page loads (optional)
                // window.print();
            });
        </script>
    </body>
    </html>
    """
    
    return Response(html, mimetype='text/html')

@app.route('/export_groups')
@login_required
def export_groups():
    program_id = request.args.get('program_id')
    if not program_id:
        flash('Program ID is required', 'error')
        return redirect(url_for('index'))
        
    program = manager.get_program(program_id)
    if not program:
        flash('Program not found', 'error')
        return redirect(url_for('index'))
        
    if not program.groups:
        flash('No groups to export', 'warning')
        return redirect(url_for('index', program_id=program_id))
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{program.name.replace(' ', '_')}_groups_{timestamp}.xlsx"
        output = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with pd.ExcelWriter(output) as writer:
            # Create a summary sheet
            summary_data = []
            for group_id, group in program.groups.items():
                summary_data.append({
                    'Group ID': group_id,
                    'Group Name': group.name,
                    'Student Count': len(group.student_ids),
                    'Instructor': group.instructor,
                    'Notes': group.notes
                })
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Create a sheet for each group
            for group_id, group in program.groups.items():
                group_students = []
                for student_id in group.student_ids:
                    if student_id in program.students:
                        student = program.students[student_id]
                        group_students.append({
                            'Student ID': student.customer_id,
                            'Name': student.name,
                            'Age': student.age,
                            'Ability': student.ability_level,
                            'Emergency Contact': student.emergency_contact,
                            'Emergency Phone': student.emergency_phone,
                            'Notes': '; '.join([note['text'] for note in student.notes]) if hasattr(student, 'notes') else ''
                        })
                
                if group_students:
                    # Ensure sheet name is valid (max 31 chars, no invalid chars)
                    sheet_name = f"{group_id} {group.name}"[:31]
                    sheet_name = "".join(c if c.isalnum() or c in ' _-' else '_' for c in sheet_name)
                    pd.DataFrame(group_students).to_excel(writer, sheet_name=sheet_name, index=False)
        
        return send_file(output, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Error exporting groups: {str(e)}', 'error')
        return redirect(url_for('index', program_id=program_id))

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')
    
    # Open the browser after the server starts
    Timer(1, open_browser).start()
    
    # Run the app with debug mode and reloader
    app.run(debug=True, use_reloader=False)
