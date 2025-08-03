import websocket
import json
import threading
import time
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

class WebSocketClient:
    """WebSocket client for Angel One real-time data streaming"""
    
    def __init__(self, api_key: str, client_id: str, access_token: str, feed_token: str = None):
        self.api_key = api_key
        self.client_id = client_id
        self.access_token = access_token
        self.feed_token = feed_token or access_token  # Use access token as fallback
        self.ws_url = f"wss://smartapisocket.angelone.in/smart-stream?clientCode={client_id}&feedToken={feed_token or access_token}&apiKey={api_key}"
        self.ws = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
        self.callbacks = {}
        self.subscribed_symbols = set()
        self.thread = None
        self.stop_thread = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Connect to WebSocket"""
        try:
            # Log connection attempt with masked credentials
            self.logger.info(f"Attempting WebSocket connection to {self.ws_url}")
            self.logger.info(f"Client ID: {self.client_id}")
            self.logger.info(f"API Key: {self.api_key[:8]}...")
            self.logger.info(f"Feed Token: {self.feed_token[:8] if self.feed_token else 'None'}...")
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header={
                    "Authorization": f"Bearer {self.access_token}",
                    "x-api-key": self.api_key,
                    "x-client-code": self.client_id,
                    "x-feed-token": self.feed_token
                },
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.is_connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            return self.is_connected
            
        except Exception as e:
            self.logger.error(f"WebSocket connection error: {str(e)}")
            return False
    
    def on_open(self, ws):
        """WebSocket connection opened"""
        self.logger.info("WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0
        
        # Subscribe to previously subscribed symbols
        if self.subscribed_symbols:
            self.subscribe_to_symbols(list(self.subscribed_symbols))
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Handle different message types
            if "type" in data:
                if data["type"] == "ltp":
                    self.handle_ltp_data(data)
                elif data["type"] == "ohlc":
                    self.handle_ohlc_data(data)
                elif data["type"] == "depth":
                    self.handle_depth_data(data)
                elif data["type"] == "error":
                    self.logger.error(f"WebSocket error: {data}")
                else:
                    self.logger.info(f"Unknown message type: {data}")
            else:
                self.logger.info(f"Received message: {data}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Message handling error: {str(e)}")
    
    def on_error(self, ws, error):
        """WebSocket error handler"""
        error_str = str(error)
        self.logger.error(f"WebSocket error: {error_str}")
        
        # Check for authentication errors
        if "401" in error_str or "Unauthorized" in error_str or "Authentication Failed" in error_str:
            self.logger.error("WebSocket authentication failed. Please check your credentials and tokens.")
            self.logger.error("Make sure your Angel One API credentials are correct and tokens are not expired.")
        
        self.is_connected = False
    
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        self.logger.info(f"WebSocket disconnected: {close_status_code} - {close_msg}")
        self.is_connected = False
        
        # Attempt to reconnect
        if not self.stop_thread and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect()
    
    def reconnect(self):
        """Attempt to reconnect to WebSocket"""
        self.reconnect_attempts += 1
        self.logger.info(f"Attempting to reconnect... (Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        time.sleep(self.reconnect_delay)
        
        if self.connect():
            self.logger.info("Reconnection successful")
        else:
            self.logger.error("Reconnection failed")
    
    def subscribe_to_symbols(self, symbols: List[str]) -> bool:
        """
        Subscribe to symbols for real-time data
        
        Args:
            symbols: List of symbols to subscribe to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_connected:
                self.logger.error("WebSocket not connected")
                return False
            
            # Create token list for Angel One WebSocket format
            nse_tokens = []
            bse_tokens = []
            
            for symbol in symbols:
                token_info = self.get_token_for_symbol(symbol)
                if token_info['exchange'] == 'NSE':
                    nse_tokens.append(token_info['token'])
                elif token_info['exchange'] == 'BSE':
                    bse_tokens.append(token_info['token'])
            
            # Build token list according to Angel One format
            token_list = []
            if nse_tokens:
                token_list.append({
                    "exchangeType": 1,  # NSE
                    "tokens": nse_tokens
                })
            if bse_tokens:
                token_list.append({
                    "exchangeType": 5,  # BSE
                    "tokens": bse_tokens
                })
            
            # Create subscription request
            subscribe_data = {
                "correlationID": f"sub_{int(time.time())}",
                "action": 1,  # Subscribe
                "params": {
                    "mode": 1,  # LTP mode
                    "tokenList": token_list
                }
            }
            
            self.logger.info(f"Sending subscription: {json.dumps(subscribe_data, indent=2)}")
            self.ws.send(json.dumps(subscribe_data))
            
            # Add to subscribed symbols
            self.subscribed_symbols.update(symbols)
            
            self.logger.info(f"Subscribed to symbols: {symbols}")
            return True
            
        except Exception as e:
            self.logger.error(f"Subscribe error: {str(e)}")
            return False
    
    def unsubscribe_from_symbols(self, symbols: List[str]) -> bool:
        """
        Unsubscribe from symbols
        
        Args:
            symbols: List of symbols to unsubscribe from
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_connected:
                return False
            
            # Create token list for Angel One WebSocket format
            nse_tokens = []
            bse_tokens = []
            
            for symbol in symbols:
                token_info = self.get_token_for_symbol(symbol)
                if token_info['exchange'] == 'NSE':
                    nse_tokens.append(token_info['token'])
                elif token_info['exchange'] == 'BSE':
                    bse_tokens.append(token_info['token'])
            
            # Build token list according to Angel One format
            token_list = []
            if nse_tokens:
                token_list.append({
                    "exchangeType": 1,  # NSE
                    "tokens": nse_tokens
                })
            if bse_tokens:
                token_list.append({
                    "exchangeType": 5,  # BSE
                    "tokens": bse_tokens
                })
            
            # Create unsubscription request
            unsubscribe_data = {
                "correlationID": f"unsub_{int(time.time())}",
                "action": 0,  # Unsubscribe
                "params": {
                    "mode": 1,  # LTP mode
                    "tokenList": token_list
                }
            }
            
            self.logger.info(f"Sending unsubscription: {json.dumps(unsubscribe_data, indent=2)}")
            self.ws.send(json.dumps(unsubscribe_data))
            
            # Remove from subscribed symbols
            self.subscribed_symbols.difference_update(symbols)
            
            self.logger.info(f"Unsubscribed from symbols: {symbols}")
            return True
            
        except Exception as e:
            self.logger.error(f"Unsubscribe error: {str(e)}")
            return False
    
    def get_token_for_symbol(self, symbol: str) -> Dict[str, str]:
        """Get token for symbol with exchange information"""
        symbol_token_map = {
            "NIFTY": {"token": "99926000", "exchange": "NSE", "name": "NIFTY"},
            "BANKNIFTY": {"token": "99926009", "exchange": "NSE", "name": "BANKNIFTY"},
            "SENSEX": {"token": "99919000", "exchange": "BSE", "name": "SENSEX"},
            # Add more mappings as needed
        }
        return symbol_token_map.get(symbol, {"token": "1", "exchange": "NSE", "name": symbol})
    
    def handle_ltp_data(self, data: Dict[str, Any]):
        """Handle LTP (Last Traded Price) data"""
        try:
            if "data" in data:
                for item in data["data"]:
                    symbol = item.get("symbol")
                    ltp = item.get("ltp")
                    change = item.get("change")
                    change_percent = item.get("changePercent")
                    
                    if symbol and ltp:
                        # Call registered callback
                        if "ltp_callback" in self.callbacks:
                            self.callbacks["ltp_callback"](symbol, {
                                "ltp": ltp,
                                "change": change,
                                "change_percent": change_percent,
                                "timestamp": datetime.now().isoformat()
                            })
                        
                        self.logger.debug(f"LTP Update - {symbol}: ₹{ltp} ({change_percent:+.2f}%)")
                        
        except Exception as e:
            self.logger.error(f"LTP data handling error: {str(e)}")
    
    def handle_ohlc_data(self, data: Dict[str, Any]):
        """Handle OHLC (Open, High, Low, Close) data"""
        try:
            if "data" in data:
                for item in data["data"]:
                    symbol = item.get("symbol")
                    open_price = item.get("open")
                    high_price = item.get("high")
                    low_price = item.get("low")
                    close_price = item.get("close")
                    volume = item.get("volume")
                    
                    if symbol and close_price:
                        # Call registered callback
                        if "ohlc_callback" in self.callbacks:
                            self.callbacks["ohlc_callback"](symbol, {
                                "open": open_price,
                                "high": high_price,
                                "low": low_price,
                                "close": close_price,
                                "volume": volume,
                                "timestamp": datetime.now().isoformat()
                            })
                        
                        self.logger.debug(f"OHLC Update - {symbol}: O:{open_price} H:{high_price} L:{low_price} C:{close_price}")
                        
        except Exception as e:
            self.logger.error(f"OHLC data handling error: {str(e)}")
    
    def handle_depth_data(self, data: Dict[str, Any]):
        """Handle market depth data"""
        try:
            if "data" in data:
                for item in data["data"]:
                    symbol = item.get("symbol")
                    depth_data = item.get("depth")
                    
                    if symbol and depth_data:
                        # Call registered callback
                        if "depth_callback" in self.callbacks:
                            self.callbacks["depth_callback"](symbol, depth_data)
                        
                        self.logger.debug(f"Depth Update - {symbol}")
                        
        except Exception as e:
            self.logger.error(f"Depth data handling error: {str(e)}")
    
    def register_callback(self, callback_type: str, callback: Callable):
        """
        Register callback for data updates
        
        Args:
            callback_type: Type of callback (ltp_callback, ohlc_callback, depth_callback)
            callback: Callback function
        """
        self.callbacks[callback_type] = callback
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        self.stop_thread = True
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=5)
        self.is_connected = False
        self.logger.info("WebSocket disconnected")
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.is_connected
    
    def get_subscribed_symbols(self) -> List[str]:
        """Get list of currently subscribed symbols"""
        return list(self.subscribed_symbols)
    
    def validate_credentials(self) -> bool:
        """Validate WebSocket credentials"""
        if not self.api_key or self.api_key == "your_api_key_here":
            self.logger.error("Invalid API key")
            return False
        
        if not self.client_id or self.client_id == "your_client_id_here":
            self.logger.error("Invalid client ID")
            return False
        
        if not self.access_token:
            self.logger.error("Invalid access token")
            return False
        
        if not self.feed_token:
            self.logger.error("Invalid feed token")
            return False
        
        self.logger.info("Credentials validation passed")
        return True 