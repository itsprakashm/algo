from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from models.trade import Trade
from utils.angel_one_api import AngelOneAPI
from utils.telegram_bot import TelegramBot

class TradingService:
    """Service for handling trading operations"""
    
    def __init__(self, angel_api: AngelOneAPI, telegram_bot: TelegramBot, db):
        self.angel_api = angel_api
        self.telegram_bot = telegram_bot
        self.db = db
    
    def place_trade(self, symbol: str, trade_type: str, quantity: int, 
                   entry_price: float, stop_loss: float = None, target: float = None,
                   trading_mode: str = 'PAPER') -> Optional[Trade]:
        """
        Place a new trade
        
        Args:
            symbol: Stock symbol
            trade_type: BUY/SELL
            quantity: Quantity
            entry_price: Entry price
            stop_loss: Stop loss price
            target: Target price
            trading_mode: PAPER/LIVE
        
        Returns:
            Trade object if successful, None otherwise
        """
        try:
            # Create trade record
            trade = Trade(
                symbol=symbol,
                trade_type=trade_type,
                quantity=quantity,
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_price=target,
                current_stop_loss=stop_loss,
                current_target=target,
                trading_mode=trading_mode
            )
            
            # Add to database
            self.db.session.add(trade)
            self.db.session.commit()
            
            # Place order via Angel One API if LIVE mode
            if trading_mode == 'LIVE':
                order_result = self._place_live_order(trade)
                if order_result:
                    trade.order_id = order_result.get('orderId')
                    trade.angel_order_id = order_result.get('angelOrderId')
                    self.db.session.commit()
            
            # Send Telegram alert
            if self.telegram_bot:
                self.telegram_bot.send_trade_entry(
                    symbol=symbol,
                    trade_type=trade_type,
                    quantity=quantity,
                    entry_price=entry_price,
                    stop_loss=stop_loss or 0,
                    target=target or 0
                )
            
            return trade
            
        except Exception as e:
            print(f"Place trade error: {str(e)}")
            if self.telegram_bot:
                self.telegram_bot.send_error_alert(str(e), "TradingService")
            return None
    
    def close_trade(self, trade_id: int, exit_price: float, exit_reason: str = 'MANUAL') -> bool:
        """
        Close a trade
        
        Args:
            trade_id: Trade ID
            exit_price: Exit price
            exit_reason: Exit reason
        
        Returns:
            True if successful, False otherwise
        """
        try:
            trade = Trade.query.get(trade_id)
            if not trade:
                return False
            
            # Close trade
            trade.close_trade(exit_price, exit_reason)
            
            # Place exit order if LIVE mode
            if trade.trading_mode == 'LIVE':
                self._place_exit_order(trade, exit_price)
            
            # Update database
            self.db.session.commit()
            
            # Send Telegram alert
            if self.telegram_bot:
                self.telegram_bot.send_trade_exit(
                    symbol=trade.symbol,
                    trade_type=trade.trade_type,
                    quantity=trade.quantity,
                    entry_price=float(trade.entry_price),
                    exit_price=exit_price,
                    pnl=float(trade.pnl) if trade.pnl else 0,
                    exit_reason=exit_reason
                )
            
            return True
            
        except Exception as e:
            print(f"Close trade error: {str(e)}")
            if self.telegram_bot:
                self.telegram_bot.send_error_alert(str(e), "TradingService")
            return False
    
    def update_trade_stop_loss(self, trade_id: int, new_stop_loss: float) -> bool:
        """
        Update stop loss for a trade
        
        Args:
            trade_id: Trade ID
            new_stop_loss: New stop loss price
        
        Returns:
            True if successful, False otherwise
        """
        try:
            trade = Trade.query.get(trade_id)
            if not trade:
                return False
            
            trade.update_stop_loss(new_stop_loss)
            self.db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Update stop loss error: {str(e)}")
            return False
    
    def update_trade_target(self, trade_id: int, new_target: float) -> bool:
        """
        Update target for a trade
        
        Args:
            trade_id: Trade ID
            new_target: New target price
        
        Returns:
            True if successful, False otherwise
        """
        try:
            trade = Trade.query.get(trade_id)
            if not trade:
                return False
            
            trade.update_target(new_target)
            self.db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Update target error: {str(e)}")
            return False
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades"""
        try:
            return Trade.query.filter_by(status='OPEN').all()
        except Exception as e:
            print(f"Get open trades error: {str(e)}")
            return []
    
    def check_stop_loss_hit(self, symbol: str, current_price: float) -> List[Trade]:
        """
        Check if any trades hit stop loss
        
        Args:
            symbol: Stock symbol
            current_price: Current price
        
        Returns:
            List of trades that hit stop loss
        """
        try:
            open_trades = Trade.query.filter_by(symbol=symbol, status='OPEN').all()
            hit_trades = []
            
            for trade in open_trades:
                if trade.current_stop_loss:
                    if trade.trade_type == 'BUY' and current_price <= trade.current_stop_loss:
                        hit_trades.append(trade)
                    elif trade.trade_type == 'SELL' and current_price >= trade.current_stop_loss:
                        hit_trades.append(trade)
            
            return hit_trades
            
        except Exception as e:
            print(f"Check stop loss hit error: {str(e)}")
            return []
    
    def check_target_hit(self, symbol: str, current_price: float) -> List[Trade]:
        """
        Check if any trades hit target
        
        Args:
            symbol: Stock symbol
            current_price: Current price
        
        Returns:
            List of trades that hit target
        """
        try:
            open_trades = Trade.query.filter_by(symbol=symbol, status='OPEN').all()
            hit_trades = []
            
            for trade in open_trades:
                if trade.current_target:
                    if trade.trade_type == 'BUY' and current_price >= trade.current_target:
                        hit_trades.append(trade)
                    elif trade.trade_type == 'SELL' and current_price <= trade.current_target:
                        hit_trades.append(trade)
            
            return hit_trades
            
        except Exception as e:
            print(f"Check target hit error: {str(e)}")
            return []
    
    def _place_live_order(self, trade: Trade) -> Optional[Dict[str, Any]]:
        """Place live order via Angel One API"""
        try:
            order_data = {
                "variety": "NORMAL",
                "tradingsymbol": trade.symbol,
                "symboltoken": self.angel_api.get_token_for_symbol(trade.symbol),
                "transactiontype": trade.trade_type,
                "exchange": "NSE",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": trade.quantity,
                "price": trade.entry_price
            }
            
            return self.angel_api.place_order(order_data)
            
        except Exception as e:
            print(f"Place live order error: {str(e)}")
            return None
    
    def _place_exit_order(self, trade: Trade, exit_price: float) -> bool:
        """Place exit order via Angel One API"""
        try:
            exit_type = "SELL" if trade.trade_type == "BUY" else "BUY"
            
            order_data = {
                "variety": "NORMAL",
                "tradingsymbol": trade.symbol,
                "symboltoken": self.angel_api.get_token_for_symbol(trade.symbol),
                "transactiontype": exit_type,
                "exchange": "NSE",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": trade.quantity,
                "price": exit_price
            }
            
            result = self.angel_api.place_order(order_data)
            return result is not None
            
        except Exception as e:
            print(f"Place exit order error: {str(e)}")
            return False
    
    def get_daily_pnl(self, date: str = None) -> Dict[str, Any]:
        """
        Get daily P&L summary
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            P&L summary
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            trades = Trade.query.filter(
                Trade.created_at >= f"{date} 00:00:00",
                Trade.created_at <= f"{date} 23:59:59"
            ).all()
            
            total_pnl = 0
            winning_trades = 0
            total_trades = len(trades)
            
            for trade in trades:
                if trade.pnl:
                    total_pnl += trade.pnl
                    if trade.pnl > 0:
                        winning_trades += 1
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'date': date,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'total_pnl': float(total_pnl),
                'win_rate': win_rate
            }
            
        except Exception as e:
            print(f"Get daily P&L error: {str(e)}")
            return {
                'date': date,
                'total_trades': 0,
                'winning_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0
            } 