"""
Snowsports Manager - Handles the core business logic for managing snowsports programs.
"""
import os
import pandas as pd
from datetime import datetime
from .models import db, Student, Group, Program, Movement, User
from werkzeug.utils import secure_filename

class SnowsportsManager:
    """Manages the core functionality for snowsports program management."""
    
    def __init__(self):
        self.allowed_extensions = {'xlsx', 'xls', 'csv'}
    
    def allowed_file(self, filename):
        """Check if the file has an allowed extension."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def process_file(self, filepath, program_id):
        """
        Process an uploaded file containing student data.
        
        Args:
            filepath (str): Path to the uploaded file
            program_id (str): ID of the program to associate students with
            
        Returns:
            tuple: (success (bool), message (str))
        """
        try:
            # Read the file based on extension
            if filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:  # CSV
                df = pd.read_csv(filepath)
                
            # Standardize column names (case-insensitive)
            df.columns = df.columns.str.strip().str.lower()
            
            # Process each row in the file
            for _, row in df.iterrows():
                self._process_student(row, program_id)
                
            db.session.commit()
            return True, "File processed successfully!"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error processing file: {str(e)}"
    
    def _process_student(self, data, program_id):
        """Process a single student's data."""
        # Extract data from the row (adjust column names as needed)
        student_data = {
            'id': str(data.get('student_id') or data.get('id')),
            'customer_id': str(data.get('customer_id', '')),
            'name': data.get('name', '').strip(),
            'birth_date': self._parse_date(data.get('birth_date')),
            'ability_level': data.get('ability_level', ''),
            'parent_name': data.get('parent_name', ''),
            'contact_email': data.get('contact_email', '').lower().strip(),
            'emergency_contact': data.get('emergency_contact', ''),
            'emergency_phone': data.get('emergency_phone', ''),
            'food_allergy': data.get('food_allergy', ''),
            'medication': data.get('medication', ''),
            'special_condition': data.get('special_condition', ''),
            'program_id': program_id
        }
        
        # Check if student already exists
        student = Student.query.get(student_data['id'])
        if not student:
            student = Student(**student_data)
            db.session.add(student)
        else:
            # Update existing student
            for key, value in student_data.items():
                setattr(student, key, value)
    
    def _parse_date(self, date_str):
        """Parse date string into a date object."""
        if not date_str or pd.isna(date_str):
            return None
        if isinstance(date_str, (int, float)):
            return datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(date_str) - 2)
        try:
            return pd.to_datetime(date_str).date()
        except:
            return None
    
    def move_student(self, student_id, from_group_id, to_group_id, user_id, reason=None):
        """
        Move a student from one group to another.
        
        Args:
            student_id (str): ID of the student to move
            from_group_id (str): ID of the source group
            to_group_id (str): ID of the destination group
            user_id (int): ID of the user performing the action
            reason (str, optional): Reason for the move
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update membership
            membership = Membership.query.filter_by(
                student_id=student_id,
                group_id=from_group_id,
                is_active=True
            ).first()
            
            if membership:
                membership.is_active = False
                membership.left_at = datetime.utcnow()
            
            # Create new membership
            new_membership = Membership(
                student_id=student_id,
                group_id=to_group_id,
                joined_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(new_membership)
            
            # Record the movement
            movement = Movement(
                student_id=student_id,
                from_group_id=from_group_id,
                to_group_id=to_group_id,
                moved_by_id=user_id,
                reason=reason
            )
            db.session.add(movement)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error moving student: {str(e)}")
            return False
