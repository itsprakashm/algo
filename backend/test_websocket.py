#!/usr/bin/env python3
"""
Test script for WebSocket connection and Angel One API credentials
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.angel_one_api import AngelOneAPI
from utils.websocket_client import WebSocketClient

def test_credentials():
    """Test Angel One API credentials"""
    print("=== Testing Angel One API Credentials ===")
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    api_key = os.getenv('API_KEY')
    client_id = os.getenv('CLIENT_ID')
    totp_secret = os.getenv('TOTP_SECRET')
    client_pin = os.getenv('CLIENT_PIN')
    
    print(f"API Key: {api_key[:8] if api_key else 'None'}...")
    print(f"Client ID: {client_id}")
    print(f"TOTP Secret: {totp_secret[:8] if totp_secret else 'None'}...")
    print(f"Client PIN: {'*' * len(client_pin) if client_pin else 'None'}")
    
    # Check if credentials are set
    if not all([api_key, client_id, totp_secret, client_pin]):
        print("❌ Missing credentials. Please set all required environment variables.")
        print("Copy env.example to .env and update with your actual credentials.")
        return False
    
    # Check if using placeholder values
    if api_key == "your_api_key_here" or client_id == "your_client_id_here":
        print("❌ Using placeholder credentials. Please update with actual Angel One credentials.")
        return False
    
    print("✅ Credentials are set")
    return True

def test_api_login():
    """Test Angel One API login"""
    print("\n=== Testing Angel One API Login ===")
    
    try:
        # Initialize API
        api = AngelOneAPI(
            api_key=os.getenv('API_KEY'),
            client_id=os.getenv('CLIENT_ID'),
            totp_secret=os.getenv('TOTP_SECRET'),
            client_pin=os.getenv('CLIENT_PIN')
        )
        
        # Attempt login
        if api.login():
            print("✅ API login successful")
            print(f"Access Token: {api.access_token[:20] if api.access_token else 'None'}...")
            return api
        else:
            print("❌ API login failed")
            return None
            
    except Exception as e:
        print(f"❌ API login error: {str(e)}")
        return None

def test_websocket_connection(api):
    """Test WebSocket connection"""
    print("\n=== Testing WebSocket Connection ===")
    
    try:
        # Get feed token
        feed_token = api.get_feed_token()
        print(f"Feed Token: {feed_token[:20] if feed_token else 'None'}...")
        
        # Initialize WebSocket client
        ws_client = WebSocketClient(
            api_key=os.getenv('API_KEY'),
            client_id=os.getenv('CLIENT_ID'),
            access_token=api.access_token,
            feed_token=feed_token
        )
        
        # Validate credentials
        if not ws_client.validate_credentials():
            print("❌ WebSocket credentials validation failed")
            return False
        
        # Test connection
        if ws_client.connect():
            print("✅ WebSocket connection successful")
            ws_client.disconnect()
            return True
        else:
            print("❌ WebSocket connection failed")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket test error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Angel One WebSocket Connection Test")
    print("=" * 40)
    
    # Test credentials
    if not test_credentials():
        return
    
    # Test API login
    api = test_api_login()
    if not api:
        return
    
    # Test WebSocket connection
    test_websocket_connection(api)
    
    print("\n=== Test Summary ===")
    print("If all tests passed, your WebSocket connection should work.")
    print("If any test failed, please check the error messages above.")

if __name__ == "__main__":
    main() 