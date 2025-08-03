import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class TelegramBot:
    """Telegram bot for sending trading alerts"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message to Telegram chat
        
        Args:
            message: Message to send
            parse_mode: Parse mode (HTML, Markdown)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    return True
                else:
                    print(f"Telegram send failed: {result.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"Telegram request failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Telegram send error: {str(e)}")
            return False
    
    def send_trade_signal(self, symbol: str, signal_type: str, price: float, 
                         indicators: Dict[str, Any], reason: str = "") -> bool:
        """
        Send trade signal alert
        
        Args:
            symbol: Stock symbol
            signal_type: BUY/SELL
            price: Current price
            indicators: Technical indicators data
            reason: Signal reason
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create emoji based on signal type
            emoji = "🟢" if signal_type == "BUY" else "🔴"
            
            # Format indicators
            indicator_text = ""
            if indicators:
                if "rsi" in indicators and indicators["rsi"]:
                    indicator_text += f"RSI: {indicators['rsi']:.2f}\n"
                if "macd" in indicators and indicators["macd"]:
                    indicator_text += f"MACD: {indicators['macd']:.4f}\n"
                if "vwap" in indicators and indicators["vwap"]:
                    indicator_text += f"VWAP: {indicators['vwap']:.2f}\n"
                if "supertrend" in indicators and indicators["supertrend"]:
                    indicator_text += f"Supertrend: {indicators['supertrend']}\n"
            
            message = f"""
{emoji} <b>TRADE SIGNAL ALERT</b> {emoji}

📈 <b>Symbol:</b> {symbol}
🎯 <b>Signal:</b> {signal_type}
💰 <b>Price:</b> ₹{price:.2f}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

📊 <b>Indicators:</b>
{indicator_text}

💡 <b>Reason:</b> {reason}

#TradingAlert #{symbol} #{signal_type}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Send trade signal error: {str(e)}")
            return False
    
    def send_trade_entry(self, symbol: str, trade_type: str, quantity: int, 
                        entry_price: float, stop_loss: float, target: float) -> bool:
        """
        Send trade entry alert
        
        Args:
            symbol: Stock symbol
            trade_type: BUY/SELL
            quantity: Quantity
            entry_price: Entry price
            stop_loss: Stop loss price
            target: Target price
        
        Returns:
            True if successful, False otherwise
        """
        try:
            emoji = "🟢" if trade_type == "BUY" else "🔴"
            
            message = f"""
{emoji} <b>TRADE ENTRY</b> {emoji}

📈 <b>Symbol:</b> {symbol}
🎯 <b>Type:</b> {trade_type}
📊 <b>Quantity:</b> {quantity}
💰 <b>Entry Price:</b> ₹{entry_price:.2f}
🛑 <b>Stop Loss:</b> ₹{stop_loss:.2f}
🎯 <b>Target:</b> ₹{target:.2f}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

#TradeEntry #{symbol} #{trade_type}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Send trade entry error: {str(e)}")
            return False
    
    def send_trade_exit(self, symbol: str, trade_type: str, quantity: int,
                       entry_price: float, exit_price: float, pnl: float,
                       exit_reason: str) -> bool:
        """
        Send trade exit alert
        
        Args:
            symbol: Stock symbol
            trade_type: BUY/SELL
            quantity: Quantity
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/Loss
            exit_reason: Exit reason
        
        Returns:
            True if successful, False otherwise
        """
        try:
            emoji = "🟢" if pnl > 0 else "🔴"
            pnl_emoji = "📈" if pnl > 0 else "📉"
            
            message = f"""
{emoji} <b>TRADE EXIT</b> {emoji}

📈 <b>Symbol:</b> {symbol}
🎯 <b>Type:</b> {trade_type}
📊 <b>Quantity:</b> {quantity}
💰 <b>Entry Price:</b> ₹{entry_price:.2f}
💵 <b>Exit Price:</b> ₹{exit_price:.2f}
{pnl_emoji} <b>P&L:</b> ₹{pnl:.2f}
📝 <b>Exit Reason:</b> {exit_reason}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

#TradeExit #{symbol} #{trade_type}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Send trade exit error: {str(e)}")
            return False
    
    def send_volatile_stock_alert(self, symbol: str, ltp: float, change_percent: float,
                                 volatility_score: float, signal_triggered: bool = False) -> bool:
        """
        Send volatile stock alert
        
        Args:
            symbol: Stock symbol
            ltp: Last traded price
            change_percent: Percentage change
            volatility_score: Volatility score
            signal_triggered: Whether signal is triggered
        
        Returns:
            True if successful, False otherwise
        """
        try:
            emoji = "🚨" if signal_triggered else "📊"
            signal_text = "SIGNAL TRIGGERED!" if signal_triggered else "High Volatility"
            
            message = f"""
{emoji} <b>VOLATILE STOCK ALERT</b> {emoji}

📈 <b>Symbol:</b> {symbol}
💰 <b>LTP:</b> ₹{ltp:.2f}
📊 <b>Change:</b> {change_percent:+.2f}%
🔥 <b>Volatility Score:</b> {volatility_score:.2f}
🎯 <b>Status:</b> {signal_text}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

#VolatileStock #{symbol}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Send volatile stock alert error: {str(e)}")
            return False
    
    def send_daily_summary(self, total_trades: int, winning_trades: int,
                          total_pnl: float, win_rate: float) -> bool:
        """
        Send daily trading summary
        
        Args:
            total_trades: Total number of trades
            winning_trades: Number of winning trades
            total_pnl: Total P&L
            win_rate: Win rate percentage
        
        Returns:
            True if successful, False otherwise
        """
        try:
            emoji = "📈" if total_pnl > 0 else "📉"
            
            message = f"""
📊 <b>DAILY TRADING SUMMARY</b> 📊

📈 <b>Total Trades:</b> {total_trades}
✅ <b>Winning Trades:</b> {winning_trades}
📊 <b>Win Rate:</b> {win_rate:.1f}%
{emoji} <b>Total P&L:</b> ₹{total_pnl:.2f}
📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

#DailySummary #TradingReport
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Send daily summary error: {str(e)}")
            return False
    
    def send_error_alert(self, error_message: str, component: str = "System") -> bool:
        """
        Send error alert
        
        Args:
            error_message: Error message
            component: Component where error occurred
        
        Returns:
            True if successful, False otherwise
        """
        try:
            message = f"""
⚠️ <b>ERROR ALERT</b> ⚠️

🔧 <b>Component:</b> {component}
❌ <b>Error:</b> {error_message}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

#ErrorAlert #{component}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Send error alert error: {str(e)}")
            return False 