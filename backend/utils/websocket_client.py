import websocket
import json
import threading
import time
import logging
from typing import Dict, List, Callable, Any
from datetime import datetime

class WebSocketClient:
    """WebSocket client for Angel One real-time data streaming"""

    def __init__(self, api_key: str, client_id: str, jwt_token: str, feed_token: str):
        self.api_key = api_key
        self.client_id = client_id
        self.jwt_token = jwt_token
        self.feed_token = feed_token
        self.ws_url = f"wss://smartapisocket.angelone.in/smart-stream?clientCode={client_id}&feedToken={feed_token}&apiKey={api_key}"
        self.ws = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
        self.callbacks = {}
        self.subscribed_symbols = set()
        self.thread = None
        self.stop_thread = False

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Connect to WebSocket"""
        try:
            headers = [
                f"Authorization: Bearer {self.jwt_token}",
                f"x-api-key: {self.api_key}",
                f"x-client-code: {self.client_id}",
                f"x-feed-token: {self.feed_token}"
            ]
            self.logger.info(f"Connecting to {self.ws_url}")
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header=headers,
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
        self.logger.info("WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0

        # Start heartbeat thread
        threading.Thread(target=self._heartbeat, daemon=True).start()

        # Subscribe to previously subscribed symbols
        if self.subscribed_symbols:
            self.subscribe_to_symbols(list(self.subscribed_symbols))

    def _heartbeat(self):
        while self.is_connected and not self.stop_thread:
            try:
                self.ws.send("ping")
            except Exception as e:
                self.logger.error(f"Heartbeat error: {str(e)}")
            time.sleep(30)

    def on_message(self, ws, message):
        try:
            print(f"WebSocket raw message: {message}")
            data = json.loads(message)
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
        except Exception as e:
            self.logger.error(f"Message handling error: {str(e)}")

    def on_error(self, ws, error):
        self.logger.error(f"WebSocket error: {error}")
        self.is_connected = False

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info(f"WebSocket disconnected: {close_status_code} - {close_msg}")
        self.is_connected = False
        if not self.stop_thread and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect()

    def reconnect(self):
        self.reconnect_attempts += 1
        self.logger.info(f"Attempting to reconnect... (Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        time.sleep(self.reconnect_delay)
        if self.connect():
            self.logger.info("Reconnection successful")
        else:
            self.logger.error("Reconnection failed")

    def subscribe_to_symbols(self, symbols: List[str]) -> bool:
        try:
            if not self.is_connected:
                self.logger.error("WebSocket not connected")
                return False

            token_list = []
            for symbol in symbols:
                token_info = self.get_token_for_symbol(symbol)
                token_list.append({
                    "exchangeType": 1 if token_info['exchange'] == 'NSE' else 5,
                    "token": token_info['token']
                })

            subscribe_data = {
                "action": 2,
                "data": {
                    "mode": "FULL",  # or "LTP"
                    "tokenList": token_list
                }
            }
            self.logger.info(f"Sending subscription: {json.dumps(subscribe_data, indent=2)}")
            self.ws.send(json.dumps(subscribe_data))
            self.subscribed_symbols.update(symbols)
            self.logger.info(f"Subscribed to symbols: {symbols}")
            return True

        except Exception as e:
            self.logger.error(f"Subscribe error: {str(e)}")
            return False

    def unsubscribe_from_symbols(self, symbols: List[str]) -> bool:
        try:
            if not self.is_connected:
                return False

            token_list = []
            for symbol in symbols:
                token_info = self.get_token_for_symbol(symbol)
                token_list.append({
                    "exchangeType": 1 if token_info['exchange'] == 'NSE' else 5,
                    "token": token_info['token']
                })

            unsubscribe_data = {
                "action": 3,
                "data": {
                    "mode": "FULL",  # or "LTP"
                    "tokenList": token_list
                }
            }
            self.logger.info(f"Sending unsubscription: {json.dumps(unsubscribe_data, indent=2)}")
            self.ws.send(json.dumps(unsubscribe_data))
            self.subscribed_symbols.difference_update(symbols)
            self.logger.info(f"Unsubscribed from symbols: {symbols}")
            return True

        except Exception as e:
            self.logger.error(f"Unsubscribe error: {str(e)}")
            return False

    def get_token_for_symbol(self, symbol: str) -> Dict[str, str]:
        symbol_token_map = {
            "NIFTY": {"token": "99926000", "exchange": "NSE", "name": "NIFTY"},
            "BANKNIFTY": {"token": "99926009", "exchange": "NSE", "name": "BANKNIFTY"},
            "SENSEX": {"token": "99919000", "exchange": "BSE", "name": "SENSEX"},
            # Add more mappings as needed
        }
        return symbol_token_map.get(symbol, {"token": "1", "exchange": "NSE", "name": symbol})

    def handle_ltp_data(self, data: Dict[str, Any]):
        try:
            if "data" in data:
                for item in data["data"]:
                    symbol = item.get("symbol")
                    ltp = item.get("ltp")
                    change = item.get("change")
                    change_percent = item.get("changePercent")
                    if symbol and ltp:
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
        try:
            if "data" in data:
                for item in data["data"]:
                    symbol = item.get("symbol")
                    depth_data = item.get("depth")
                    if symbol and depth_data:
                        if "depth_callback" in self.callbacks:
                            self.callbacks["depth_callback"](symbol, depth_data)
                        self.logger.debug(f"Depth Update - {symbol}")
        except Exception as e:
            self.logger.error(f"Depth data handling error: {str(e)}")

    def register_callback(self, callback_type: str, callback: Callable):
        self.callbacks[callback_type] = callback

    def disconnect(self):
        self.stop_thread = True
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=5)
        self.is_connected = False
        self.logger.info("WebSocket disconnected")

    def get_subscribed_symbols(self) -> List[str]:
        return list(self.subscribed_symbols)

    def validate_credentials(self) -> bool:
        if not self.api_key or self.api_key == "your_api_key_here":
            self.logger.error("Invalid API key")
            return False
        if not self.client_id or self.client_id == "your_client_id_here":
            self.logger.error("Invalid client ID")
            return False
        if not self.jwt_token:
            self.logger.error("Invalid JWT token")
            return False
        if not self.feed_token:
            self.logger.error("Invalid feed token")
            return False
        self.logger.info("Credentials validation passed")
        return True