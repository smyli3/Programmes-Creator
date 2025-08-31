from datetime import datetime
from src.db.database import db
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text, UniqueConstraint, DateTime, Boolean
from sqlalchemy.orm import relationship

class Student(db.Model):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)                # internal id
    customer_id = Column(Integer, unique=True, index=True)
    name = Column(String)                                 # "Last, First"
    birthdate = Column(Date)
    age_at_start = Column(Float)
    ability_start = Column(String)                        # parsed code e.g. IZ1
    parent_name = Column(String)
    email = Column(String)
    emergency_name = Column(String)
    emergency_phone = Column(String)
    food_allergy = Column(Text)
    drug_allergy = Column(Text)
    medication = Column(Text)
    notes = Column(Text)                                  # SpecialCondition etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = relationship("Membership", back_populates="student")
    progress = relationship("Progress", back_populates="student")

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'name': self.name,
            'ability_start': self.ability_start,
            'parent_name': self.parent_name,
            'email': self.email
        }

class Group(db.Model):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, index=True)                     # e.g. "IZ1-3"
    ability = Column(String)
    instructor = Column(String)                           # editable
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = relationship("Membership", back_populates="group")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'ability': self.ability,
            'instructor': self.instructor
        }

class Membership(db.Model):
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)
    week = Column(Integer)                                # 1..6 (current roster)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="memberships")
    group = relationship("Group", back_populates="memberships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('student_id', 'week', name='uniq_student_week'),
    )

class Movement(db.Model):
    __tablename__ = "movements"
    
    id = Column(Integer, primary_key=True)
    week = Column(Integer)
    date = Column(Date, default=datetime.utcnow)
    customer_id = Column(Integer, index=True)
    student_name = Column(String)
    from_group = Column(String)
    to_group = Column(String)
    reason = Column(Text)
    entered_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'week': self.week,
            'date': self.date.isoformat(),
            'student_name': self.student_name,
            'from_group': self.from_group,
            'to_group': self.to_group,
            'reason': self.reason,
            'entered_by': self.entered_by
        }

class Progress(db.Model):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True)
    week = Column(Integer)
    customer_id = Column(Integer, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    group_at_start = Column(String)
    ability_focus = Column(Text)
    milestones = Column(Text)
    coach_notes = Column(Text)
    attendance = Column(String)                           # Present/Absent/...
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="progress")

    def to_dict(self):
        return {
            'id': self.id,
            'week': self.week,
            'customer_id': self.customer_id,
            'student_id': self.student_id,
            'group_at_start': self.group_at_start,
            'ability_focus': self.ability_focus,
            'milestones': self.milestones,
            'coach_notes': self.coach_notes,
            'attendance': self.attendance
        }
