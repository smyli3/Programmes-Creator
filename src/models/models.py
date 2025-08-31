from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

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

@dataclass
class Group:
    """Represents a group of students with an instructor."""
    group_id: str
    name: str
    program_id: str
    instructor: str = ""
    notes: str = ""
    student_ids: List[str] = field(default_factory=list)

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

    def to_dict(self):
        return {
            'program_id': self.program_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'active': self.active,
            'students': {k: v.__dict__ for k, v in self.students.items()},
            'groups': {k: v.__dict__ for k, v in self.groups.items()}
        }
