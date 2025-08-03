from datetime import datetime
from db import db

class VolatileStock(db.Model):
    """Volatile stock model for tracking high volatility stocks"""
    
    __tablename__ = 'volatile_stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Price Data
    ltp = db.Column(db.Numeric(10, 2), nullable=False)
    change = db.Column(db.Numeric(10, 2), nullable=True)
    change_percent = db.Column(db.Numeric(5, 2), nullable=True)
    
    # Volatility Metrics
    volatility_score = db.Column(db.Numeric(5, 2), nullable=True)  # Combined volatility score
    price_volatility = db.Column(db.Numeric(5, 2), nullable=True)  # Price volatility percentage
    volume_spike = db.Column(db.Numeric(5, 2), nullable=True)  # Volume spike ratio
    
    # Candle Analysis
    candle_body_size = db.Column(db.Numeric(5, 2), nullable=True)
    candle_wick_size = db.Column(db.Numeric(5, 2), nullable=True)
    is_breakout = db.Column(db.Boolean, default=False)
    is_momentum = db.Column(db.Boolean, default=False)
    
    # Technical Indicators
    rsi = db.Column(db.Numeric(5, 2), nullable=True)
    macd = db.Column(db.Numeric(10, 4), nullable=True)
    macd_signal = db.Column(db.Numeric(10, 4), nullable=True)
    vwap = db.Column(db.Numeric(10, 2), nullable=True)
    supertrend_signal = db.Column(db.String(10), nullable=True)
    
    # Signal Generation
    signal_triggered = db.Column(db.Boolean, default=False)
    signal_type = db.Column(db.String(10), nullable=True)  # BUY, SELL
    signal_strength = db.Column(db.Numeric(5, 2), nullable=True)  # Signal strength (0-100)
    
    # Volume Data
    volume = db.Column(db.BigInteger, nullable=True)
    volume_sma = db.Column(db.Numeric(15, 2), nullable=True)
    volume_ratio = db.Column(db.Numeric(5, 2), nullable=True)
    
    # Ranking
    rank = db.Column(db.Integer, nullable=True)  # Rank among volatile stocks
    
    def __init__(self, symbol, ltp, **kwargs):
        self.symbol = symbol
        self.ltp = ltp
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_volatility_score(self):
        """Calculate combined volatility score"""
        score = 0
        
        # Price volatility component (40% weight)
        if self.price_volatility:
            score += self.price_volatility * 0.4
        
        # Volume spike component (30% weight)
        if self.volume_spike:
            score += min(self.volume_spike, 10) * 3  # Cap at 10x volume
        
        # Candle body size component (20% weight)
        if self.candle_body_size:
            score += self.candle_body_size * 0.2
        
        # Change percentage component (10% weight)
        if self.change_percent:
            score += abs(self.change_percent) * 0.1
        
        self.volatility_score = score
    
    def check_breakout_pattern(self, previous_data=None):
        """Check for breakout patterns"""
        if not previous_data:
            return
        
        # Check for strong breakout candle
        if (self.candle_body_size and self.candle_body_size > 60 and
            self.volume_ratio and self.volume_ratio > 1.5):
            self.is_breakout = True
        
        # Check for momentum continuation
        if (self.change_percent and abs(self.change_percent) > 2 and
            self.volume_ratio and self.volume_ratio > 1.2):
            self.is_momentum = True
    
    def generate_signal(self):
        """Generate trading signal based on indicators"""
        signal_score = 0
        signal_type = None
        
        # RSI conditions
        if self.rsi:
            if self.rsi < 30:  # Oversold
                signal_score += 25
                signal_type = 'BUY'
            elif self.rsi > 70:  # Overbought
                signal_score += 25
                signal_type = 'SELL'
        
        # MACD conditions
        if self.macd and self.macd_signal:
            if self.macd > self.macd_signal:  # Bullish crossover
                signal_score += 20
                if not signal_type:
                    signal_type = 'BUY'
            elif self.macd < self.macd_signal:  # Bearish crossover
                signal_score += 20
                if not signal_type:
                    signal_type = 'SELL'
        
        # Supertrend conditions
        if self.supertrend_signal:
            if self.supertrend_signal == 'BUY':
                signal_score += 25
                if not signal_type:
                    signal_type = 'BUY'
            elif self.supertrend_signal == 'SELL':
                signal_score += 25
                if not signal_type:
                    signal_type = 'SELL'
        
        # Volume confirmation
        if self.volume_ratio and self.volume_ratio > 1.5:
            signal_score += 15
        
        # Breakout confirmation
        if self.is_breakout:
            signal_score += 15
        
        # Set signal if score is high enough
        if signal_score >= 50:
            self.signal_triggered = True
            self.signal_type = signal_type
            self.signal_strength = signal_score
    
    def to_dict(self):
        """Convert volatile stock to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ltp': float(self.ltp) if self.ltp else None,
            'change': float(self.change) if self.change else None,
            'change_percent': float(self.change_percent) if self.change_percent else None,
            'volatility_score': float(self.volatility_score) if self.volatility_score else None,
            'price_volatility': float(self.price_volatility) if self.price_volatility else None,
            'volume_spike': float(self.volume_spike) if self.volume_spike else None,
            'candle_body_size': float(self.candle_body_size) if self.candle_body_size else None,
            'candle_wick_size': float(self.candle_wick_size) if self.candle_wick_size else None,
            'is_breakout': self.is_breakout,
            'is_momentum': self.is_momentum,
            'rsi': float(self.rsi) if self.rsi else None,
            'macd': float(self.macd) if self.macd else None,
            'macd_signal': float(self.macd_signal) if self.macd_signal else None,
            'vwap': float(self.vwap) if self.vwap else None,
            'supertrend_signal': self.supertrend_signal,
            'signal_triggered': self.signal_triggered,
            'signal_type': self.signal_type,
            'signal_strength': float(self.signal_strength) if self.signal_strength else None,
            'volume': int(self.volume) if self.volume else None,
            'volume_sma': float(self.volume_sma) if self.volume_sma else None,
            'volume_ratio': float(self.volume_ratio) if self.volume_ratio else None,
            'rank': self.rank
        }
    
    def __repr__(self):
        return f'<VolatileStock {self.symbol} {self.volatility_score}>' 