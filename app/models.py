from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
from . import db

# Association table for many-to-many relationship between users and roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

class Role(db.Model):
    """Role model for user permissions."""
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'

    @staticmethod
    def insert_roles():
        """Insert default roles if they don't exist."""
        roles = {
            'admin': 'Administrator with full access',
            'instructor': 'Can manage programs and groups',
            'user': 'Regular user with limited access'
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r, description=roles[r])
                db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)

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

class Movement(db.Model):
    """Tracks student movements between groups."""
    __tablename__ = 'movements'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'))
    from_group_id = db.Column(db.String(36), db.ForeignKey('groups.id'), nullable=True)
    to_group_id = db.Column(db.String(36), db.ForeignKey('groups.id'), nullable=True)
    moved_at = db.Column(db.DateTime, default=datetime.utcnow)
    moved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='movements')
    from_group = db.relationship('Group', foreign_keys=[from_group_id])
    to_group = db.relationship('Group', foreign_keys=[to_group_id])
    moved_by = db.relationship('User')
    
    def __repr__(self):
        return f'<Movement {self.student.name} from {self.from_group_id} to {self.to_group_id}>'


class Note(db.Model):
    """Notes about students."""
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'))
    content = db.Column(db.Text)
    author = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)
