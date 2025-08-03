#!/usr/bin/env python3
"""
Script to fix admin user password
"""

from app import app, db
from models.user import User
from werkzeug.security import generate_password_hash

def fix_admin_password():
    """Fix admin user password"""
    try:
        with app.app_context():
            # Find admin user
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("❌ Admin user not found!")
                return False
            
            print(f"✅ Found admin user: {admin_user.username}")
            
            # Update password hash
            admin_user.password_hash = generate_password_hash('admin123')
            db.session.commit()
            
            print("✅ Admin password updated successfully!")
            
            # Verify the password works
            if admin_user.check_password('admin123'):
                print("✅ Password verification successful!")
                return True
            else:
                print("❌ Password verification failed!")
                return False
            
    except Exception as e:
        print(f"❌ Error fixing admin password: {str(e)}")
        return False

if __name__ == "__main__":
    fix_admin_password() 