import requests
import json
import time
import pyotp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class AngelOneAPI:
    """Angel One SmartAPI integration class"""
    
    def __init__(self, api_key: str, client_id: str, totp_secret: str, client_pin: str):
        self.api_key = api_key
        self.client_id = client_id
        self.totp_secret = totp_secret
        self.client_pin = client_pin
        self.base_url = "https://apiconnect.angelbroking.com"
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.feed_token = None
        self.token_expiry = None
        
    def generate_totp(self) -> str:
        """Generate TOTP for authentication"""
        totp = pyotp.TOTP(self.totp_secret)
        return totp.now()
    
    def login(self) -> bool:
        """Login to Angel One API"""
        try:
            totp = self.generate_totp()
            
            login_data = {
                "clientcode": self.client_id,
                "password": self.client_pin,
                "totp": totp
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-UserType": "USER",
                "X-SourceID": "WEB",
                "X-ClientLocalIP": "CLIENT_LOCAL_IP",
                "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
                "X-MACAddress": "MAC_ADDRESS",
                "X-PrivateKey": self.api_key
            }
            
            response = self.session.post(
                f"{self.base_url}/rest/auth/angelbroking/user/v1/loginByPassword",
                json=login_data,
                headers=headers
            )
            print(response.status_code, response.text)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    self.access_token = data["data"]["jwtToken"]
                    self.refresh_token = data["data"]["refreshToken"]
                    # Extract feed token from login response
                    self.feed_token = data["data"].get("feedToken")
                    # Set token expiry (typically 24 hours)
                    self.token_expiry = datetime.now() + timedelta(hours=24)
                    return True
                else:
                    print(f"Login failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"Login request failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        try:
            if not self.refresh_token:
                return self.login()
            
            refresh_data = {
                "refreshToken": self.refresh_token
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-UserType": "USER",
                "X-SourceID": "WEB",
                "X-ClientLocalIP": "CLIENT_LOCAL_IP",
                "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
                "X-MACAddress": "MAC_ADDRESS",
                "X-PrivateKey": self.api_key
            }
            
            response = self.session.post(
                f"{self.base_url}/rest/auth/angelbroking/jwt/v1/generateTokens",
                json=refresh_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    self.access_token = data["data"]["jwtToken"]
                    self.refresh_token = data["data"]["refreshToken"]
                    self.token_expiry = datetime.now() + timedelta(hours=24)
                    return True
                else:
                    print(f"Token refresh failed: {data.get('message', 'Unknown error')}")
                    return self.login()
            else:
                print(f"Token refresh request failed with status code: {response.status_code}")
                return self.login()
                
        except Exception as e:
            print(f"Token refresh error: {str(e)}")
            return self.login()
    
    def ensure_token_valid(self) -> bool:
        """Ensure access token is valid, refresh if needed"""
        if not self.access_token:
            return self.login()
        
        if self.token_expiry and datetime.now() >= self.token_expiry:
            return self.refresh_access_token()
        
        return True
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB"
        }
    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            if not self.ensure_token_valid():
                return None
            
            response = self.session.get(
                f"{self.base_url}/rest/secure/angelbroking/user/v1/getUserProfile",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    return data["data"]
                else:
                    print(f"Get profile failed: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Get profile request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Get profile error: {str(e)}")
            return None
    
    def get_market_data(self, symbols: List[str]) -> Optional[List[Dict[str, Any]]]:
        """Get market data for symbols"""
        try:
            if not self.ensure_token_valid():
                return None
            
            # Convert symbols to Angel One format
            formatted_symbols = []
            for symbol in symbols:
                # Add exchange and token mapping logic here
                formatted_symbols.append({
                    "exchangeType": "NSE",
                    "symbol": symbol,
                    "token": self.get_token_for_symbol(symbol)
                })
            
            market_data = {
                "mode": "LTP",
                "exchangeTokens": formatted_symbols
            }
            
            response = self.session.post(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/getLtpData",
                json=market_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    return data["data"]["ltpData"]
                else:
                    print(f"Get market data failed: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Get market data request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Get market data error: {str(e)}")
            return None
    
    def get_token_for_symbol(self, symbol: str) -> str:
        """Get token for symbol (simplified mapping)"""
        # This is a simplified mapping. In production, you'd need a proper symbol-to-token mapping
        symbol_token_map = {
            "NIFTY": "26000",
            "BANKNIFTY": "26009",
            "SENSEX": "19000",
            # Add more mappings as needed
        }
        return symbol_token_map.get(symbol, "1")
    
    def place_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Place order via Angel One API"""
        try:
            if not self.ensure_token_valid():
                return None
            
            response = self.session.post(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/placeOrder",
                json=order_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    return data["data"]
                else:
                    print(f"Place order failed: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Place order request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Place order error: {str(e)}")
            return None
    
    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order status"""
        try:
            if not self.ensure_token_valid():
                return None
            
            order_status_data = {
                "orderId": order_id
            }
            
            response = self.session.post(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/getOrderBook",
                json=order_status_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    return data["data"]
                else:
                    print(f"Get order status failed: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Get order status request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Get order status error: {str(e)}")
            return None
    
    def get_holdings(self) -> Optional[List[Dict[str, Any]]]:
        """Get current holdings"""
        try:
            if not self.ensure_token_valid():
                return None
            
            response = self.session.get(
                f"{self.base_url}/rest/secure/angelbroking/portfolio/v1/getHolding",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    return data["data"]
                else:
                    print(f"Get holdings failed: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Get holdings request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Get holdings error: {str(e)}")
            return None
    
    def get_positions(self) -> Optional[List[Dict[str, Any]]]:
        """Get current positions"""
        try:
            if not self.ensure_token_valid():
                return None
            
            response = self.session.get(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/getPosition",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    return data["data"]
                else:
                    print(f"Get positions failed: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Get positions request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Get positions error: {str(e)}")
            return None
    
    def get_feed_token(self) -> Optional[str]:
        """Get feed token for WebSocket connection"""
        # Return the feed token that was extracted during login
        if self.feed_token:
            print(f"Using feed token from login: {self.feed_token[:10]}...")
            return self.feed_token
        else:
            print("No feed token available from login, using access token as fallback")
            return self.access_token 