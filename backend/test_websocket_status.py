#!/usr/bin/env python3
"""
Test script to check WebSocket client status
"""

from app import app, websocket_client

def test_websocket_status():
    """Test WebSocket client status"""
    try:
        with app.app_context():
            print("=== WebSocket Client Status Test ===")
            
            if websocket_client:
                print(f"✅ WebSocket client exists")
                print(f"   Connected: {websocket_client.is_connected()}")
                print(f"   Subscribed symbols: {websocket_client.get_subscribed_symbols()}")
                
                # Test the WebSocket status endpoint
                from flask import request
                from flask_jwt_extended import create_access_token
                from models.user import User
                
                # Create a test token
                admin_user = User.query.filter_by(username='admin').first()
                if admin_user:
                    token = create_access_token(identity=str(admin_user.id))
                    print(f"✅ Test token created: {token[:20]}...")
                    
                    # Test the endpoint
                    with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
                        from app import websocket_status
                        response = websocket_status()
                        print(f"✅ WebSocket status endpoint response: {response}")
                else:
                    print("❌ Admin user not found")
            else:
                print("❌ WebSocket client is None")
                print("   This means the Angel One API login failed or credentials are invalid")
                
    except Exception as e:
        print(f"❌ Error testing WebSocket status: {str(e)}")

if __name__ == "__main__":
    test_websocket_status() 