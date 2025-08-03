import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'algo_trading')
    
    # Angel One API Configuration
    API_KEY = os.getenv('API_KEY')
    CLIENT_ID = os.getenv('CLIENT_ID')
    TOTP_SECRET = os.getenv('TOTP_SECRET')
    CLIENT_PIN = os.getenv('CLIENT_PIN')
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Admin Credentials
    DEFAULT_ADMIN_USER = os.getenv('DEFAULT_ADMIN_USER', 'user')
    DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'user123')
    
    # Trading Configuration
    DEFAULT_CANDLE_INTERVAL = int(os.getenv('DEFAULT_CANDLE_INTERVAL', '1'))
    PAPER_TRADING_MODE = os.getenv('PAPER_TRADING_MODE', 'true').lower() == 'true'
    MAX_VOLATILE_STOCKS = int(os.getenv('MAX_VOLATILE_STOCKS', '10'))
    
    # Technical Indicators Configuration
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    MACD_FAST = int(os.getenv('MACD_FAST', '12'))
    MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))
    SUPERTREND_PERIOD = int(os.getenv('SUPERTREND_PERIOD', '10'))
    SUPERTREND_MULTIPLIER = float(os.getenv('SUPERTREND_MULTIPLIER', '3'))
    VWAP_PERIOD = int(os.getenv('VWAP_PERIOD', '20'))
    
    # Risk Management
    DEFAULT_RISK_REWARD_RATIO = float(os.getenv('DEFAULT_RISK_REWARD_RATIO', '1.5'))
    TRAILING_STOP_PERCENTAGE = float(os.getenv('TRAILING_STOP_PERCENTAGE', '0.5'))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '1000'))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '10000'))
    
    # WebSocket Configuration
    WEBSOCKET_RECONNECT_DELAY = 5  # seconds
    WEBSOCKET_MAX_RECONNECT_ATTEMPTS = 10
    
    # Database URL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'algo_trading')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 