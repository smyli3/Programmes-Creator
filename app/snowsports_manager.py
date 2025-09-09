"""
Snowsports Manager - Handles the core business logic for managing snowsports programs.
"""
import os
import pandas as pd
from datetime import datetime
from uuid import uuid4
from .models import db, Student, Group, Program, Movement, User, Membership
from werkzeug.utils import secure_filename

class SnowsportsManager:
    """Manages the core functionality for snowsports program management."""
    
    def __init__(self):
        self.allowed_extensions = {'xlsx', 'xls', 'csv'}
    
    def allowed_file(self, filename):
        """Check if the file has an allowed extension."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def create_groups_weekly(self, program_id, week_number, max_group_size=8):
        """Create groups for a specific week and assign weekly memberships.

        Rules:
        - Normalize ability codes (e.g., FT, BZ1, BZ2, IZ, AZ) with common aliases
        - Group students by ability; within each ability, sort by age (birth_date)
        - Create descriptive group names including ability code
        - Handle unclassified students in a 'MIXED' bucket
        """
        program = Program.query.get(program_id)
        if not program:
            raise ValueError("Program not found")
        students = Student.query.filter_by(program_id=program_id).all()
        if not students:
            raise ValueError("No students found in program")

        # Clear existing memberships for this week for all groups in this program
        Membership.query.filter(
            db.and_(
                Membership.group_id.in_(db.session.query(Group.id).filter_by(program_id=program_id)),
                Membership.week_number == week_number
            )
        ).delete(synchronize_session=False)

        # If week 1, reset groups
        if week_number == 1:
            # Remove memberships (already cleared for week 1 above), then groups
            Group.query.filter_by(program_id=program_id).delete()
            db.session.flush()

        # Ability normalization map
        def norm_ability(val: str) -> str:
            v = (val or '').strip().upper()
            aliases = {
                'FT': {'FT', 'FIRST TIMER', 'FIRST-TIMER', 'BEGINNER0', 'B0'},
                'BZ1': {'BZ1', 'BEGINNER1', 'B1', 'BEGINNER 1'},
                'BZ2': {'BZ2', 'BEGINNER2', 'B2', 'BEGINNER 2'},
                'IZ': {'IZ', 'INTERMEDIATE', 'INT', 'I'},
                'AZ': {'AZ', 'ADVANCED', 'ADV', 'A'},
            }
            for key, vals in aliases.items():
                if v in vals:
                    return key
            # If matches base keys already
            if v in aliases.keys():
                return v
            # Fallbacks for common product description dumps
            if v.startswith('BZ') and len(v) == 3 and v[2].isdigit():
                return v  # e.g., BZ1/BZ2
            if v in {'', 'UNKNOWN', 'N/A', 'NA', 'NONE'}:
                return 'MIXED'
            return v  # keep as-is but bucketed separately

        # Group students by normalized ability, sort by age (birth_date oldest to youngest)
        from collections import defaultdict
        ability_groups = defaultdict(list)
        for s in students:
            ability = norm_ability(getattr(s, 'ability_level', '') or '')
            ability_groups[ability].append(s)
        for ability in ability_groups:
            # Sort by birth_date ascending (older first) to form balanced groups by age
            ability_groups[ability].sort(key=lambda s: (s.birth_date or datetime.min))

        import math
        groups_created = 0
        # Iterate abilities in a deterministic order
        for ability_level in sorted(ability_groups.keys()):
            ability_students = ability_groups[ability_level]
            num_groups = math.ceil(len(ability_students) / max_group_size) if max_group_size > 0 else 0

            # Pre-create or reuse groups for this ability
            groups_for_ability = []
            for i in range(num_groups):
                if week_number == 1:
                    group = Group(
                        id=str(uuid4()),
                        name=f"{ability_level} Group {i + 1}",
                        program_id=program_id,
                        ability_level=ability_level,
                        max_size=max_group_size,
                    )
                    db.session.add(group)
                    db.session.flush()
                    groups_created += 1
                else:
                    # Reuse existing group for this ability/index if possible
                    group = Group.query.filter_by(program_id=program_id, ability_level=ability_level).order_by(Group.name).offset(i).first()
                    if not group:
                        group = Group(
                            id=str(uuid4()),
                            name=f"{ability_level} Group {i + 1}",
                            program_id=program_id,
                            ability_level=ability_level,
                            max_size=max_group_size,
                        )
                        db.session.add(group)
                        db.session.flush()
                        groups_created += 1
                groups_for_ability.append(group)

            # Balanced distribution: snake ordering then round-robin to groups
            # Create a snake sequence (oldest, youngest, 2nd oldest, 2nd youngest, ...)
            snake_order = []
            left, right = 0, len(ability_students) - 1
            toggle = True
            while left <= right:
                if toggle:
                    snake_order.append(ability_students[left])
                    left += 1
                else:
                    snake_order.append(ability_students[right])
                    right -= 1
                toggle = not toggle

            # Assign round-robin to groups respecting capacity
            gi = 0
            capacities = {g.id: g.max_size or max_group_size for g in groups_for_ability}
            for st in snake_order:
                placed = False
                attempts = 0
                while not placed and attempts < max(1, len(groups_for_ability)):
                    g = groups_for_ability[gi % len(groups_for_ability)]
                    if capacities[g.id] > 0:
                        db.session.add(Membership(
                            student_id=st.id,
                            group_id=g.id,
                            week_number=week_number,
                            is_active=True,
                            joined_at=datetime.utcnow()
                        ))
                        capacities[g.id] -= 1
                        placed = True
                    gi += 1
                    attempts += 1

        db.session.commit()
        return groups_created
               
    def create_groups(self, program_id, max_group_size=6, keep_existing=False):
        """
        Create groups for a program based on student ability levels and ages.
        
        Args:
            program_id (str): ID of the program to create groups for
            max_group_size (int): Maximum number of students per group
            keep_existing (bool): If True, keep existing groups; if False, clear them first
            
        Returns:
            tuple: (success: bool, message: str)
        """
        from .models import Program, Group, Membership, db
        
        try:
            # Validate program exists and get students
            program = Program.query.get(program_id)
            if not program:
                return False, "Program not found"
                
            students = program.students.all()
            if not students:
                return False, "No students found in this program"
                
            # Clear existing groups if not keeping them
            if not keep_existing:
                # First get all group IDs for this program
                group_ids = [g.id for g in Group.query.filter_by(program_id=program_id).with_entities(Group.id).all()]
                
                # Delete memberships in those groups
                if group_ids:
                    Membership.query.filter(Membership.group_id.in_(group_ids)).delete(synchronize_session=False)
                
                # Then delete the groups
                Group.query.filter_by(program_id=program_id).delete()
                db.session.commit()
            
            # Group students by ability level
            from collections import defaultdict
            from datetime import datetime
            
            # First, normalize ability levels
            ability_groups = defaultdict(list)
            for student in students:
                # Simple normalization - extract first word of ability_level
                ability = (student.ability_level or 'Beginner').split()[0].lower()
                ability_groups[ability].append(student)
            
            # Sort each ability group by age (youngest first)
            for ability in ability_groups:
                ability_groups[ability].sort(key=lambda s: s.birth_date or datetime.min)
            
            # Create groups
            group_count = 0
            for ability, students_in_ability in ability_groups.items():
                # Split into chunks of max_group_size
                for i in range(0, len(students_in_ability), max_group_size):
                    group_students = students_in_ability[i:i + max_group_size]
                    group_count += 1
                    
                    # Create group
                    group = Group(
                        id=str(uuid4()),
                        program_id=program_id,
                        name=f"{ability.capitalize()} {group_count}",
                        max_size=max_group_size
                    )
                    db.session.add(group)
                    
                    # Add students to group
                    for student in group_students:
                        membership = Membership(
                            student_id=student.id,
                            group_id=group.id,
                            joined_at=datetime.utcnow(),
                            is_active=True
                        )
                        db.session.add(membership)
            
            db.session.commit()
            return True, f"Created {group_count} groups for {len(students)} students"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating groups: {str(e)}"
    
    def process_file(self, filepath, program_id, duplicate_strategy='skip'):
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
                
            # Standardize column names (case-insensitive) and normalize to snake_case
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(r"[^a-z0-9]+", "_", regex=True)
                .str.strip("_")
            )
            
            # Process each row in the file
            processed = 0
            created = 0
            updated = 0
            skipped = 0
            for _, row in df.iterrows():
                result = self._process_student(row, program_id, duplicate_strategy)
                processed += 1
                if result == 'created':
                    created += 1
                elif result == 'updated':
                    updated += 1
                elif result == 'skipped':
                    skipped += 1
                
            db.session.commit()
            return True, f"Processed {processed} rows • created {created}, updated {updated}, skipped {skipped}."
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error processing file: {str(e)}"
    
    def _process_student(self, data, program_id, duplicate_strategy='skip'):
        """Process a single student's data.
        Returns one of: 'created' | 'updated' | 'skipped'
        duplicate_strategy: 'skip' | 'update' | 'duplicate'
        """
        # Normalize alternative column names
        def first_nonempty(*keys):
            for k in keys:
                v = data.get(k)
                if v is not None and not (isinstance(v, float) and pd.isna(v)) and str(v).strip() != '':
                    return v
            return None

        # ID: prefer explicit id, else customer_id, else generate uuid
        raw_id = first_nonempty('student_id', 'id')
        # Accept various aliases for customer id
        customer_id = first_nonempty('customer_id', 'customerid', 'customer_number', 'customer number', 'cust_id')
        student_id = str(raw_id or customer_id or '')
        if not student_id:
            student_id = str(uuid4())

        # Name: prefer full name, else compose from first/last; handle 'last, first'
        name = first_nonempty('name', 'full_name', 'full name', 'customername')
        if not name:
            first = first_nonempty('first_name', 'first name', 'given_name') or ''
            last = first_nonempty('last_name', 'last name', 'surname') or ''
            name = f"{str(first).strip()} {str(last).strip()}".strip()
        else:
            # If in 'Last, First' format, flip it
            if isinstance(name, str) and ',' in name:
                parts = [p.strip() for p in name.split(',', 1)]
                if len(parts) == 2:
                    name = f"{parts[1]} {parts[0]}".strip()

        # Ability: accept variations, infer from productdescription_1 if present
        ability = first_nonempty('ability_level', 'ability', 'level', 'skill_level', 'productdescription_1') or ''

        # Compose student_data
        student_data = {
            'id': student_id,
            'customer_id': str(customer_id or ''),
            'name': str(name or '').strip(),
            'birth_date': self._parse_date(first_nonempty('birth_date', 'dob', 'date_of_birth')),
            'ability_level': str(ability),
            'parent_name': str(first_nonempty('parent_name', 'guardian', 'parent') or ''),
            # Prefer textbox37 (actual email) over textbox71 (HOH/Guest flag)
            'contact_email': str(first_nonempty('textbox37', 'contact_email', 'email', 'textbox71') or '').lower().strip(),
            'emergency_contact': str(first_nonempty('emergency_contact', 'emergency contact', 'primaryemergencycontact') or ''),
            'emergency_phone': str(first_nonempty('emergency_phone', 'emergency phone', 'emergency_phone_number', 'primaryemergencyphone') or ''),
            'food_allergy': str(first_nonempty('food_allergy', 'allergy', 'allergies') or first_nonempty('foodallergy') or ''),
            'medication': str(first_nonempty('medication', 'medications', 'drugallergy') or ''),
            'special_condition': str(first_nonempty('special_condition', 'notes', 'special_needs') or first_nonempty('specialcondition') or ''),
            'program_id': program_id
        }

        # Clean sentinel values for contact_email
        if student_data['contact_email'] in {'hoh', 'guest'}:
            student_data['contact_email'] = ''
        
        # Determine lookup keys for deduplication
        # Priority: explicit ID (student_id) -> customer_id -> (name + birth_date) -> contact_email
        existing = None
        if student_data['id']:
            existing = Student.query.get(student_data['id'])
        if not existing and student_data.get('customer_id'):
            existing = Student.query.filter_by(customer_id=student_data['customer_id']).first()
        if not existing and student_data.get('name') and student_data.get('birth_date'):
            existing = Student.query.filter_by(name=student_data['name'], birth_date=student_data['birth_date']).first()
        if not existing and student_data.get('contact_email'):
            existing = Student.query.filter_by(contact_email=student_data['contact_email']).first()

        # Apply duplicate strategy
        if existing:
            if duplicate_strategy == 'skip':
                return 'skipped'
            elif duplicate_strategy == 'update':
                for key, value in student_data.items():
                    setattr(existing, key, value)
                return 'updated'
            else:  # 'duplicate'
                # Force a new unique ID
                student_data['id'] = str(uuid4())
                student = Student(**student_data)
                db.session.add(student)
                return 'created'
        else:
            student = Student(**student_data)
            db.session.add(student)
            return 'created'
    
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
