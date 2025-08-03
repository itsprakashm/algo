from datetime import datetime
from db import db

class MarketData(db.Model):
    """Market data model for storing real-time price data"""
    
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # OHLCV Data
    open_price = db.Column(db.Numeric(10, 2), nullable=False)
    high_price = db.Column(db.Numeric(10, 2), nullable=False)
    low_price = db.Column(db.Numeric(10, 2), nullable=False)
    close_price = db.Column(db.Numeric(10, 2), nullable=False)
    volume = db.Column(db.BigInteger, nullable=True)
    
    # Additional Data
    ltp = db.Column(db.Numeric(10, 2), nullable=True)  # Last Traded Price
    change = db.Column(db.Numeric(10, 2), nullable=True)  # Price Change
    change_percent = db.Column(db.Numeric(5, 2), nullable=True)  # Percentage Change
    
    # Technical Indicators
    rsi = db.Column(db.Numeric(5, 2), nullable=True)
    macd = db.Column(db.Numeric(10, 4), nullable=True)
    macd_signal = db.Column(db.Numeric(10, 4), nullable=True)
    macd_histogram = db.Column(db.Numeric(10, 4), nullable=True)
    vwap = db.Column(db.Numeric(10, 2), nullable=True)
    supertrend = db.Column(db.Numeric(10, 2), nullable=True)
    supertrend_signal = db.Column(db.String(10), nullable=True)  # BUY, SELL
    
    # Candle Analysis
    candle_body_size = db.Column(db.Numeric(5, 2), nullable=True)  # Body size as percentage
    candle_wick_size = db.Column(db.Numeric(5, 2), nullable=True)  # Wick size as percentage
    is_doji = db.Column(db.Boolean, default=False)
    is_hammer = db.Column(db.Boolean, default=False)
    is_shooting_star = db.Column(db.Boolean, default=False)
    
    # Volume Analysis
    volume_sma = db.Column(db.Numeric(15, 2), nullable=True)  # Volume Simple Moving Average
    volume_ratio = db.Column(db.Numeric(5, 2), nullable=True)  # Current volume / Average volume
    
    # Interval
    interval = db.Column(db.String(10), default='1min')  # 1min, 3min, 5min, 1day
    
    def __init__(self, symbol, open_price, high_price, low_price, close_price, **kwargs):
        self.symbol = symbol
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_candle_analysis(self):
        """Calculate candle pattern analysis"""
        if self.high_price and self.low_price and self.open_price and self.close_price:
            # Calculate body and wick sizes
            body_size = abs(self.close_price - self.open_price)
            total_range = self.high_price - self.low_price
            
            if total_range > 0:
                self.candle_body_size = (body_size / total_range) * 100
                self.candle_wick_size = ((total_range - body_size) / total_range) * 100
            
            # Identify patterns
            body_threshold = 0.1  # 10% of total range
            wick_threshold = 0.6  # 60% of total range
            
            if self.candle_body_size and self.candle_body_size < body_threshold:
                self.is_doji = True
            
            # Hammer pattern (small body, long lower wick)
            if (self.candle_body_size and self.candle_body_size < 0.3 and 
                self.close_price > self.open_price and 
                (self.low_price - min(self.open_price, self.close_price)) / total_range > 0.6):
                self.is_hammer = True
            
            # Shooting star pattern (small body, long upper wick)
            if (self.candle_body_size and self.candle_body_size < 0.3 and 
                self.close_price < self.open_price and 
                (self.high_price - max(self.open_price, self.close_price)) / total_range > 0.6):
                self.is_shooting_star = True
    
    def calculate_change(self, previous_close=None):
        """Calculate price change and percentage"""
        if previous_close and self.close_price:
            self.change = self.close_price - previous_close
            if previous_close > 0:
                self.change_percent = (self.change / previous_close) * 100
    
    def to_dict(self):
        """Convert market data to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'open_price': float(self.open_price) if self.open_price else None,
            'high_price': float(self.high_price) if self.high_price else None,
            'low_price': float(self.low_price) if self.low_price else None,
            'close_price': float(self.close_price) if self.close_price else None,
            'volume': int(self.volume) if self.volume else None,
            'ltp': float(self.ltp) if self.ltp else None,
            'change': float(self.change) if self.change else None,
            'change_percent': float(self.change_percent) if self.change_percent else None,
            'rsi': float(self.rsi) if self.rsi else None,
            'macd': float(self.macd) if self.macd else None,
            'macd_signal': float(self.macd_signal) if self.macd_signal else None,
            'macd_histogram': float(self.macd_histogram) if self.macd_histogram else None,
            'vwap': float(self.vwap) if self.vwap else None,
            'supertrend': float(self.supertrend) if self.supertrend else None,
            'supertrend_signal': self.supertrend_signal,
            'candle_body_size': float(self.candle_body_size) if self.candle_body_size else None,
            'candle_wick_size': float(self.candle_wick_size) if self.candle_wick_size else None,
            'is_doji': self.is_doji,
            'is_hammer': self.is_hammer,
            'is_shooting_star': self.is_shooting_star,
            'volume_sma': float(self.volume_sma) if self.volume_sma else None,
            'volume_ratio': float(self.volume_ratio) if self.volume_ratio else None,
            'interval': self.interval
        }
    
    def __repr__(self):
        return f'<MarketData {self.symbol} {self.timestamp}>' 