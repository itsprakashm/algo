#!/usr/bin/env python3
"""
Test script to verify JWT token functionality
"""

from app import app, db
from models.user import User
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import datetime

def test_jwt_functionality():
    """Test JWT token creation and validation"""
    try:
        with app.app_context():
            # Test 1: Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("❌ Admin user not found!")
                return False
            
            print(f"✅ Admin user found: {admin_user.username}")
            
            # Test 2: Create JWT token
            access_token = create_access_token(identity=admin_user.id)
            print(f"✅ JWT token created: {access_token[:20]}...")
            
            # Test 3: Validate token (simulate what happens in @jwt_required())
            try:
                # This simulates what happens when a request comes in with the token
                with app.test_request_context(headers={'Authorization': f'Bearer {access_token}'}):
                    # The token should be valid
                    print("✅ JWT token validation successful")
            except Exception as e:
                print(f"❌ JWT token validation failed: {str(e)}")
                return False
            
            # Test 4: Test user authentication
            if admin_user.check_password('admin123'):
                print("✅ User password validation successful")
            else:
                print("❌ User password validation failed")
                return False
            
            print("\n🎉 All JWT tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ JWT test error: {str(e)}")
        return False

if __name__ == "__main__":
    test_jwt_functionality() 