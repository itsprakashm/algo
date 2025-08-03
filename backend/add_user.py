#!/usr/bin/env python3
"""
Script to add a new user to the database
"""

from werkzeug.security import generate_password_hash
from app import app, db
from models.user import User

def add_user(username, password, email=None, is_admin=False):
    """Add a new user to the database"""
    try:
        with app.app_context():
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"User '{username}' already exists!")
                return False
            
            # Create new user
            user = User(
                username=username,
                password=password,
                email=email or f"{username}@algo-trading.com",
                is_admin=is_admin
            )
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            print(f"User '{username}' created successfully!")
            return True
            
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False

if __name__ == "__main__":
    # Add the requested user
    username = "prakash"
    password = "prakash@123"
    
    success = add_user(username, password)
    
    if success:
        print(f"\nUser credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"\nYou can now login with these credentials!")
    else:
        print("Failed to create user. Please check the error message above.") 