from datetime import datetime
from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Program(db.Model):
    """Program model for snowsports programs."""
    __tablename__ = 'programs'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    students = db.relationship('Student', backref='program', lazy='dynamic')
    groups = db.relationship('Group', backref='program', lazy='dynamic')

class Student(db.Model):
    """Student model for program participants."""
    __tablename__ = 'students'
    id = db.Column(db.String(36), primary_key=True)
    customer_id = db.Column(db.String(64), index=True)
    name = db.Column(db.String(128), index=True)
    birth_date = db.Column(db.Date)
    ability_level = db.Column(db.String(64))
    parent_name = db.Column(db.String(128))
    contact_email = db.Column(db.String(120))
    emergency_contact = db.Column(db.String(128))
    emergency_phone = db.Column(db.String(20))
    food_allergy = db.Column(db.Text)
    medication = db.Column(db.Text)
    special_condition = db.Column(db.Text)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'))
    
    # Relationships
    memberships = db.relationship('Membership', backref='student', lazy='dynamic')
    notes = db.relationship('Note', backref='student', lazy='dynamic')

class Group(db.Model):
    """Group model for student groups."""
    __tablename__ = 'groups'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'))
    instructor = db.Column(db.String(128))
    notes = db.Column(db.Text)
    
    # Relationships
    members = db.relationship('Membership', backref='group', lazy='dynamic')

class Membership(db.Model):
    """Association table between students and groups."""
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'))
    group_id = db.Column(db.String(36), db.ForeignKey('groups.id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class Note(db.Model):
    """Notes about students."""
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'))
    content = db.Column(db.Text)
    author = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)
