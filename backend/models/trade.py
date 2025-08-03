from datetime import datetime
from decimal import Decimal
from db import db

class Trade(db.Model):
    """Trade model for storing trade data"""
    
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    trade_type = db.Column(db.String(10), nullable=False)  # BUY/SELL
    quantity = db.Column(db.Integer, nullable=False)
    entry_price = db.Column(db.Numeric(10, 2), nullable=False)
    exit_price = db.Column(db.Numeric(10, 2), nullable=True)
    stop_loss = db.Column(db.Numeric(10, 2), nullable=True)
    target_price = db.Column(db.Numeric(10, 2), nullable=True)
    current_stop_loss = db.Column(db.Numeric(10, 2), nullable=True)
    current_target = db.Column(db.Numeric(10, 2), nullable=True)
    
    # P&L and Status
    pnl = db.Column(db.Numeric(10, 2), nullable=True)
    pnl_percentage = db.Column(db.Numeric(5, 2), nullable=True)
    status = db.Column(db.String(20), default='OPEN')  # OPEN, CLOSED, CANCELLED
    
    # Trading Mode
    trading_mode = db.Column(db.String(10), default='PAPER')  # PAPER, LIVE
    
    # Exit Information
    exit_reason = db.Column(db.String(50), nullable=True)  # SL_HIT, TARGET_HIT, TRAILING_STOP, MANUAL
    exit_time = db.Column(db.DateTime, nullable=True)
    
    # Technical Indicators
    rsi_value = db.Column(db.Numeric(5, 2), nullable=True)
    macd_value = db.Column(db.Numeric(10, 4), nullable=True)
    macd_signal = db.Column(db.Numeric(10, 4), nullable=True)
    vwap_value = db.Column(db.Numeric(10, 2), nullable=True)
    supertrend_signal = db.Column(db.String(10), nullable=True)  # BUY, SELL
    
    # Timestamps
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Order Information
    order_id = db.Column(db.String(50), nullable=True)
    angel_order_id = db.Column(db.String(50), nullable=True)
    
    def __init__(self, symbol, trade_type, quantity, entry_price, **kwargs):
        self.symbol = symbol
        self.trade_type = trade_type
        self.quantity = quantity
        self.entry_price = entry_price
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_pnl(self):
        """Calculate P&L for the trade"""
        if self.exit_price and self.entry_price:
            if self.trade_type == 'BUY':
                self.pnl = (self.exit_price - self.entry_price) * self.quantity
            else:  # SELL
                self.pnl = (self.entry_price - self.exit_price) * self.quantity
            
            # Calculate percentage
            if self.entry_price > 0:
                self.pnl_percentage = (self.pnl / (self.entry_price * self.quantity)) * 100
    
    def update_stop_loss(self, new_stop_loss):
        """Update stop loss with trailing logic"""
        if self.trade_type == 'BUY':
            if new_stop_loss > self.current_stop_loss:
                self.current_stop_loss = new_stop_loss
        else:  # SELL
            if new_stop_loss < self.current_stop_loss or self.current_stop_loss is None:
                self.current_stop_loss = new_stop_loss
    
    def update_target(self, new_target):
        """Update target price with dynamic extension"""
        if self.trade_type == 'BUY':
            if new_target > self.current_target:
                self.current_target = new_target
        else:  # SELL
            if new_target < self.current_target or self.current_target is None:
                self.current_target = new_target
    
    def close_trade(self, exit_price, exit_reason='MANUAL'):
        """Close the trade"""
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.exit_time = datetime.utcnow()
        self.status = 'CLOSED'
        self.calculate_pnl()
    
    def to_dict(self):
        """Convert trade to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'trade_type': self.trade_type,
            'quantity': self.quantity,
            'entry_price': float(self.entry_price) if self.entry_price else None,
            'exit_price': float(self.exit_price) if self.exit_price else None,
            'stop_loss': float(self.stop_loss) if self.stop_loss else None,
            'target_price': float(self.target_price) if self.target_price else None,
            'current_stop_loss': float(self.current_stop_loss) if self.current_stop_loss else None,
            'current_target': float(self.current_target) if self.current_target else None,
            'pnl': float(self.pnl) if self.pnl else None,
            'pnl_percentage': float(self.pnl_percentage) if self.pnl_percentage else None,
            'status': self.status,
            'trading_mode': self.trading_mode,
            'exit_reason': self.exit_reason,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'rsi_value': float(self.rsi_value) if self.rsi_value else None,
            'macd_value': float(self.macd_value) if self.macd_value else None,
            'macd_signal': float(self.macd_signal) if self.macd_signal else None,
            'vwap_value': float(self.vwap_value) if self.vwap_value else None,
            'supertrend_signal': self.supertrend_signal,
            'order_id': self.order_id,
            'angel_order_id': self.angel_order_id
        }
    
    def __repr__(self):
        return f'<Trade {self.symbol} {self.trade_type} {self.status}>' 