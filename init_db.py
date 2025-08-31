#!/usr/bin/env python3
"""
Initialize the database and create an admin user.
Run this script to set up the database and create an initial admin account.
"""
import os
import sys
import getpass
from werkzeug.security import generate_password_hash

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Role

def create_admin_user(email, username, password):
    """Create an admin user with the given credentials."""
    # Check if admin user already exists
    if User.query.filter_by(email=email).first():
        print(f"[!] User with email {email} already exists.")
        return False
    
    if User.query.filter_by(username=username).first():
        print(f"[!] Username {username} is already taken.")
        return False
    
    # Create admin role if it doesn't exist
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator with full access')
        db.session.add(admin_role)
        db.session.commit()
        print("[+] Created 'admin' role")
    
    # Create user role if it doesn't exist
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular user with basic access')
        db.session.add(user_role)
        db.session.commit()
        print("[+] Created 'user' role")
    
    # Create the admin user
    admin = User(
        email=email,
        username=username,
        password=password,
        is_admin=True,
        confirmed=True
    )
    
    # Add admin role to the user
    admin.roles.append(admin_role)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"[+] Created admin user: {username} ({email})")
    return True

def main():
    """Main function to initialize the database and create an admin user."""
    # Create the Flask application
    app = create_app('development')
    
    with app.app_context():
        # Create all database tables
        print("[*] Creating database tables...")
        db.create_all()
        print("[+] Database tables created successfully!")
        
        # Check if we have any users
        if User.query.first():
            print("[*] Database already contains users.")
            sys.exit(0)
        
        # Get admin user details
        print("\n=== Create Admin User ===")
        email = input("Admin email: ").strip()
        username = input("Admin username: ").strip()
        
        while True:
            password = getpass.getpass("Admin password: ").strip()
            if len(password) < 8:
                print("[!] Password must be at least 8 characters long.")
                continue
                
            confirm_password = getpass.getpass("Confirm password: ").strip()
            if password != confirm_password:
                print("[!] Passwords do not match. Please try again.")
                continue
            break
        
        # Create the admin user
        print("\n[*] Creating admin user...")
        if create_admin_user(email, username, password):
            print("[+] Admin user created successfully!")
        else:
            print("[!] Failed to create admin user.")
            sys.exit(1)

if __name__ == '__main__':
    main()
