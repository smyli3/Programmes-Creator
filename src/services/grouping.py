import pandas as pd
from datetime import datetime
import io
import xlsxwriter
from typing import Tuple, Dict, Any

def parse_inventory_date(date_str: str) -> datetime:
    """Parse inventory date from string like 'Inventory Pool Date: dd/mm/yyyy'"""
    try:
        date_part = date_str.split(':')[-1].strip()
        return datetime.strptime(date_part, '%d/%m/%Y')
    except (ValueError, AttributeError, IndexError):
        return datetime.utcnow()

def parse_birthdate(date_str: str) -> datetime:
    """Parse birthdate from string like 'dd-mmm-yy'"""
    try:
        return datetime.strptime(date_str, '%d-%b-%y')
    except (ValueError, TypeError):
        return None

def extract_ability(description: str) -> str:
    """Extract ability code from product description"""
    if not description or not isinstance(description, str):
        return "UNKNOWN"
    # Get the last token as ability code
    return description.strip().split()[-1] if description.strip() else "UNKNOWN"

def build_stage1(df: pd.DataFrame, group_size: int = 6) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, datetime]:
    """
    Process the input DataFrame and generate stage 1 grouping.
    
    Args:
        df: Input DataFrame with student data
        group_size: Maximum number of students per group
        
    Returns:
        Tuple containing:
        - summary_df: Group summary statistics
        - instructor_assign_df: Instructor assignment template
        - profiles_df: Student profiles
        - stage1_groups_df: Detailed group assignments
        - program_start_date: Program start date
    """
    # Parse dates and extract abilities
    program_start_date = None
    if 'InventoryDate' in df.columns:
        program_start_date = parse_inventory_date(df['InventoryDate'].iloc[0]) if not df.empty else datetime.utcnow()
    else:
        program_start_date = datetime.utcnow()
    
    # Clean and prepare data
    df['Ability'] = df['ProductDescription_1'].apply(extract_ability)
    
    if 'BirthDate' in df.columns:
        df['BirthDate'] = df['BirthDate'].apply(parse_birthdate)
        df['Age'] = df['BirthDate'].apply(
            lambda x: (program_start_date - x).days / 365.25 if pd.notnull(x) else 0
        )
    
    # Sort by ability, age, and name
    df_sorted = df.sort_values(by=['Ability', 'Age', 'CustomerName'])
    
    # Assign groups
    df_sorted['ProposedGroupID'] = ''
    current_group = 1
    
    for ability in df_sorted['Ability'].unique():
        ability_df = df_sorted[df_sorted['Ability'] == ability]
        num_groups = (len(ability_df) + group_size - 1) // group_size
        
        for i in range(num_groups):
            start_idx = i * group_size
            end_idx = min((i + 1) * group_size, len(ability_df))
            group_id = f"{ability}-{i+1}"
            df_sorted.loc[ability_df.iloc[start_idx:end_idx].index, 'ProposedGroupID'] = group_id
    
    # Create summary DataFrame
    summary_df = df_sorted.groupby('ProposedGroupID').agg(
        Ability=('Ability', 'first'),
        NumStudents=('CustomerID', 'count'),
        AvgAge=('Age', 'mean')
    ).reset_index()
    
    # Create instructor assignment template
    instructor_assign_df = summary_df[['ProposedGroupID', 'Ability']].copy()
    instructor_assign_df['Instructor'] = ''
    
    # Create student profiles
    profiles_df = df_sorted[[
        'CustomerID', 'CustomerName', 'BirthDate', 'Age', 'Ability',
        'ParentName', 'Email', 'EmergencyName', 'EmergencyPhone',
        'FoodAllergy', 'DrugAllergy', 'Medication', 'SpecialCondition',
        'ProposedGroupID'
    ]].copy()
    
    # Create detailed groups DataFrame
    stage1_groups_df = df_sorted[[
        'ProposedGroupID', 'CustomerID', 'CustomerName', 'Ability', 'Age',
        'ParentName', 'Email', 'EmergencyPhone'
    ]].copy()
    
    return summary_df, instructor_assign_df, profiles_df, stage1_groups_df, program_start_date

def build_stage2(stage1_groups_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create empty templates for movement log and weekly progress.
    
    Args:
        stage1_groups_df: DataFrame from build_stage1
        
    Returns:
        Tuple containing:
        - movement_log_df: Empty movement log template
        - weekly_progress_df: Empty weekly progress template
    """
    # Create empty movement log
    movement_cols = [
        'Week', 'Date', 'CustomerID', 'StudentName',
        'FromGroup', 'ToGroup', 'Reason', 'EnteredBy'
    ]
    movement_log_df = pd.DataFrame(columns=movement_cols)
    
    # Create empty weekly progress template
    progress_cols = [
        'Week', 'CustomerID', 'GroupAtStart', 'AbilityFocus',
        'Milestones', 'CoachNotes', 'Attendance'
    ]
    weekly_progress_df = pd.DataFrame(columns=progress_cols)
    
    return movement_log_df, weekly_progress_df

def pack_excel(
    summary: pd.DataFrame,
    instructor_assign: pd.DataFrame,
    profiles: pd.DataFrame,
    stage1_groups: pd.DataFrame,
    movement_log: pd.DataFrame,
    progress: pd.DataFrame
) -> io.BytesIO:
    """
    Pack all data into an Excel workbook.
    
    Args:
        summary: Group summary
        instructor_assign: Instructor assignments
        profiles: Student profiles
        stage1_groups: Detailed group assignments
        movement_log: Movement log
        progress: Weekly progress
        
    Returns:
        BytesIO object containing the Excel file
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each DataFrame to a different worksheet
        summary.to_excel(writer, sheet_name='Group Summary', index=False)
        instructor_assign.to_excel(writer, sheet_name='Instructor Assign', index=False)
        profiles.to_excel(writer, sheet_name='Student Profiles', index=False)
        stage1_groups.to_excel(writer, sheet_name='Stage 1 Groups', index=False)
        movement_log.to_excel(writer, sheet_name='Movement Log', index=False)
        progress.to_excel(writer, sheet_name='Weekly Progress', index=False)
        
        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(writer.sheets[sheet_name]._cell_args[0]):
                series = writer.sheets[sheet_name]._cell_args[1][idx][1]
                max_length = max(series.astype(str).apply(len).max(), len(series.name))
                worksheet.set_column(idx, idx, max_length + 2)
    
    output.seek(0)
    return output
