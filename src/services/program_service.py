from typing import Dict, List, Optional, Tuple
import uuid
from datetime import datetime
from ..models.models import Program, Student, Group

class ProgramService:
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

    def create_program(self, name: str, description: str = "") -> Tuple[bool, str, Optional[Program]]:
        """Create a new program."""
        try:
            program_id = str(uuid.uuid4())
            program = Program(
                program_id=program_id,
                name=name,
                description=description
            )
            self.programs[program_id] = program
            return True, "Program created successfully", program
        except Exception as e:
            return False, f"Failed to create program: {str(e)}", None

    def get_program(self, program_id: str) -> Optional[Program]:
        """Get a program by ID."""
        return self.programs.get(program_id)

    def delete_program(self, program_id: str) -> Tuple[bool, str]:
        """Delete a program."""
        if program_id in self.programs:
            del self.programs[program_id]
            return True, "Program deleted successfully"
        return False, "Program not found"

    def get_all_programs(self) -> List[Program]:
        """Get all programs."""
        return list(self.programs.values())

# Create a singleton instance
program_service = ProgramService()
