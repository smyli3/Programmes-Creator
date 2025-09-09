# Data Import Fix Instructions for ChatGPT-5 in Windsurf

## Problem Summary
- CSV upload shows "Processed 221 rows • created 0, updated 0, skipped 221" 
- Only 2 students visible in UI despite 221 rows processed
- Weekly groups view shows empty or minimal student assignments
- Likely caused by deduplication logic matching existing records with bad data

## Immediate Diagnostic Commands

### Step 1: Run Flask Shell Diagnostics
Execute these commands in the Flask shell to understand current state:

```python
# In terminal, start Flask shell
python -c "
from app import create_app
from app.extensions import db
from app.models import Program, Student, Group, Membership

app = create_app()
with app.app_context():
    print('=== PROGRAM ANALYSIS ===')
    programs = Program.query.all()
    for p in programs:
        print(f'Program: {p.name} (ID: {p.id})')
        student_count = Student.query.filter_by(program_id=p.id).count()
        print(f'  Students: {student_count}')
        
    print('\n=== DATA QUALITY ISSUES ===')
    bad_emails = Student.query.filter(Student.contact_email.in_(['hoh', 'guest'])).count()
    print(f'Students with bad sentinel emails: {bad_emails}')
    
    with_customer_id = Student.query.filter(Student.customer_id.isnot(None), Student.customer_id != '').count()
    print(f'Students with customer_id: {with_customer_id}')
    
    with_name_dob = Student.query.filter(Student.name != '', Student.birth_date.isnot(None)).count()
    print(f'Students with name+birthdate: {with_name_dob}')
    
    print('\n=== WEEKLY ASSIGNMENTS ===')
    for p in programs:
        for week in range(1, (p.max_weeks or 6) + 1):
            active_members = db.session.query(Membership).join(Group).filter(
                Group.program_id == p.id,
                Membership.week_number == week,
                Membership.is_active == True
            ).count()
            if active_members > 0:
                print(f'{p.name} Week {week}: {active_members} active assignments')
"
```

### Step 2: Identify Target Program
Get the specific program ID that should have 221 students:

```python
# Find the program you uploaded to
python -c "
from app import create_app
from app.models import Program
app = create_app()
with app.app_context():
    programs = Program.query.all()
    for p in programs:
        print(f'ID: {p.id} | Name: {p.name} | Active: {p.active}')
        print(f'  Created: {p.created_at if hasattr(p, \"created_at\") else \"N/A\"}')
        print('---')
"
```

## Fix Options (Choose One)

### Option A: Clean Re-import (Recommended)
Clear the problematic program data and re-import fresh:

```python
# Replace TARGET_PROGRAM_ID with the actual program ID from Step 2
TARGET_PROGRAM_ID = "REPLACE_WITH_ACTUAL_PROGRAM_ID"

python -c "
from app import create_app
from app.extensions import db
from app.models import Program, Student, Group, Membership

app = create_app()
with app.app_context():
    target_program_id = '${TARGET_PROGRAM_ID}'
    
    print(f'Clearing data for program: {target_program_id}')
    
    # Get all groups for this program
    group_ids = [g.id for g in Group.query.filter_by(program_id=target_program_id).all()]
    
    if group_ids:
        # Delete memberships first
        deleted_memberships = Membership.query.filter(Membership.group_id.in_(group_ids)).delete(synchronize_session=False)
        print(f'Deleted {deleted_memberships} memberships')
        
        # Delete groups
        deleted_groups = Group.query.filter_by(program_id=target_program_id).delete()
        print(f'Deleted {deleted_groups} groups')
    
    # Delete students
    deleted_students = Student.query.filter_by(program_id=target_program_id).delete()
    print(f'Deleted {deleted_students} students')
    
    db.session.commit()
    print('Program data cleared successfully')
"
```

**After running the clear command:**
1. Go to the upload page in your web interface
2. Select "Allow duplicates" or "Update existing" (NOT "Skip existing")  
3. Upload your CSV file again
4. Should show "created 221" or "updated 221"

### Option B: Force Update Existing Records
Update all existing records to refresh the data:

```python
# This will force update all students in the target program
TARGET_PROGRAM_ID = "REPLACE_WITH_ACTUAL_PROGRAM_ID"

python -c "
from app import create_app
from app.extensions import db
from app.models import Student

app = create_app()
with app.app_context():
    target_program_id = '${TARGET_PROGRAM_ID}'
    
    # Clean up bad sentinel email values
    students = Student.query.filter_by(program_id=target_program_id).all()
    updated = 0
    
    for student in students:
        if student.contact_email in ['hoh', 'guest', 'HOH', 'Guest']:
            student.contact_email = ''
            updated += 1
    
    db.session.commit()
    print(f'Cleaned {updated} bad email addresses')
    print('Now re-upload with \"Update existing\" strategy')
"
```

### Option C: Create New Program (Test)
Create a fresh program to test import without affecting existing data:

```python
# Create a test program for clean import
python -c "
from app import create_app
from app.extensions import db
from app.models import Program
from datetime import date
import uuid

app = create_app()
with app.app_context():
    test_program = Program(
        id=str(uuid.uuid4()),
        name='Test Import - $(date +%Y%m%d)',
        description='Clean test import',
        active=True,
        max_weeks=6,
        current_week=1,
        start_date=date.today()
    )
    
    db.session.add(test_program)
    db.session.commit()
    
    print(f'Created test program: {test_program.id}')
    print(f'Program name: {test_program.name}')
"
```

## Verification Commands

### After Re-import, Verify Success:

```python
# Check if import worked
TARGET_PROGRAM_ID = "REPLACE_WITH_ACTUAL_PROGRAM_ID"

python -c "
from app import create_app
from app.models import Student, Program

app = create_app()
with app.app_context():
    target_program_id = '${TARGET_PROGRAM_ID}'
    program = Program.query.get(target_program_id)
    
    if program:
        student_count = Student.query.filter_by(program_id=target_program_id).count()
        print(f'Program: {program.name}')
        print(f'Students imported: {student_count}')
        
        # Sample 5 students to verify data quality
        sample_students = Student.query.filter_by(program_id=target_program_id).limit(5).all()
        for s in sample_students:
            print(f'  - {s.name} | Age: {s.age} | Ability: {s.ability_level} | Email: {s.contact_email or \"None\"}')
    else:
        print('Program not found')
"
```

### Generate Initial Groups (If Import Successful):

```python
# Generate Week 1 groups after successful import
TARGET_PROGRAM_ID = "REPLACE_WITH_ACTUAL_PROGRAM_ID"

python -c "
from app import create_app
from app.extensions import db
from app.snowsports_manager import SnowsportsManager

app = create_app()
with app.app_context():
    target_program_id = '${TARGET_PROGRAM_ID}'
    
    try:
        manager = SnowsportsManager()
        groups_created = manager.create_groups_weekly(target_program_id, week_number=1, max_group_size=8)
        print(f'Created {groups_created} groups for Week 1')
        
        # Verify group assignments
        from app.models import Group, Membership
        groups = Group.query.filter_by(program_id=target_program_id).all()
        for group in groups:
            member_count = Membership.query.filter_by(
                group_id=group.id, 
                week_number=1, 
                is_active=True
            ).count()
            print(f'  {group.name}: {member_count}/{group.max_size} students')
            
    except Exception as e:
        print(f'Error creating groups: {e}')
"
```

## Expected Results

### Success Indicators:
- Import shows: "Processed 221 rows • created 221, updated 0, skipped 0" (or similar)
- Students page shows all 221 students for the target program
- Weekly groups page shows students distributed across groups
- No more "bad sentinel emails" in diagnostics

### If Still Having Issues:

```python
# Debug specific CSV mapping issues
python -c "
from app import create_app
from app.models import Student
import pandas as pd

app = create_app()
with app.app_context():
    # Check if data is being parsed correctly
    # Replace with path to your CSV
    csv_path = 'path/to/your/uploaded.csv'
    
    try:
        df = pd.read_csv(csv_path)
        print(f'CSV has {len(df)} rows and columns: {list(df.columns)}')
        print('\nFirst row sample:')
        print(df.iloc[0].to_dict())
        
        # Check for common mapping issues
        customer_id_col = None
        for col in df.columns:
            if 'customer' in col.lower() and 'id' in col.lower():
                customer_id_col = col
                break
        
        if customer_id_col:
            print(f'\nCustomer ID column: {customer_id_col}')
            print(f'Sample values: {df[customer_id_col].head().tolist()}')
        else:
            print('\nNo CustomerID column found!')
            
    except Exception as e:
        print(f'Error reading CSV: {e}')
"
```

## Execution Order

1. **Run diagnostic commands first** to understand current state
2. **Choose ONE fix option** (A, B, or C) based on your preference  
3. **Execute the fix commands**
4. **Re-upload your CSV** with appropriate duplicate strategy
5. **Run verification commands** to confirm success
6. **Generate groups** if everything looks good

Replace `TARGET_PROGRAM_ID` with the actual program UUID from the diagnostics, and execute these commands in your terminal within the Flask app directory.