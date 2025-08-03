from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import threading
import time

# Import configuration and models
from config import config
from models.user import User
from models.trade import Trade
from models.market_data import MarketData
from models.volatile_stock import VolatileStock
from db import db

# Import utilities
from utils.angel_one_api import AngelOneAPI
from utils.telegram_bot import TelegramBot
from utils.websocket_client import WebSocketClient
from utils.technical_indicators import *

# Import services
from services.trading_service import TradingService
from services.market_data_service import MarketDataService
from services.signal_service import SignalService

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
CORS(app)
jwt = JWTManager(app)

# Initialize database
db.init_app(app)

# Create all tables
with app.app_context():
    db.create_all()

# Initialize services
trading_service = None
market_data_service = None
signal_service = None
telegram_bot = None
websocket_client = None

def initialize_services():
    """Initialize all services"""
    global trading_service, market_data_service, signal_service, telegram_bot, websocket_client
    
    try:
        # Initialize Angel One API
        angel_api = AngelOneAPI(
            api_key=app.config['API_KEY'],
            client_id=app.config['CLIENT_ID'],
            totp_secret=app.config['TOTP_SECRET'],
            client_pin=app.config['CLIENT_PIN']
        )
        
        # Initialize Telegram Bot
        telegram_bot = TelegramBot(
            bot_token=app.config['TELEGRAM_BOT_TOKEN'],
            chat_id=app.config['TELEGRAM_CHAT_ID']
        )
        
        # Initialize services
        trading_service = TradingService(angel_api, telegram_bot, db)
        market_data_service = MarketDataService(db)
        signal_service = SignalService(db, telegram_bot)
        
        # Initialize WebSocket client
        if angel_api.login():
            # Get feed token for WebSocket connection
            feed_token = angel_api.get_feed_token()
            websocket_client = WebSocketClient(
                api_key=app.config['API_KEY'],
                client_id=app.config['CLIENT_ID'],
                access_token=angel_api.access_token,
                feed_token=feed_token
            )
            
            # Validate credentials before connecting
            if websocket_client.validate_credentials():
                # Register callbacks
                websocket_client.register_callback("ltp_callback", market_data_service.handle_ltp_update)
                websocket_client.register_callback("ohlc_callback", market_data_service.handle_ohlc_update)
                
                # Connect to WebSocket
                if websocket_client.connect():
                    # Subscribe to index symbols
                    websocket_client.subscribe_to_symbols(["NIFTY", "BANKNIFTY", "SENSEX"])
                    print("WebSocket connected and subscribed to index symbols")
                else:
                    print("Failed to connect to WebSocket")
            else:
                print("WebSocket credentials validation failed")
        else:
            print("Failed to login to Angel One API")
            
    except Exception as e:
        print(f"Service initialization error: {str(e)}")

def create_admin_user():
    """Create default admin user if not exists"""
    try:
        with app.app_context():
            admin_user = User.query.filter_by(username=app.config['DEFAULT_ADMIN_USER']).first()
            if not admin_user:
                admin_user = User(
                    username=app.config['DEFAULT_ADMIN_USER'],
                    password=app.config['DEFAULT_ADMIN_PASSWORD'],
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully")
            else:
                print("Admin user already exists")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=str(user.id))
            
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard routes
@app.route('/api/dashboard/market-data', methods=['GET'])
@jwt_required()
def get_market_data():
    """Get real-time market data for dashboard"""
    try:
        symbols = request.args.getlist('symbols')
        if not symbols:
            symbols = ["NIFTY", "BANKNIFTY", "SENSEX"]
        
        # Get latest market data from database
        market_data = []
        for symbol in symbols:
            try:
                latest_data = MarketData.query.filter_by(symbol=symbol).order_by(MarketData.timestamp.desc()).first()
                if latest_data:
                    market_data.append(latest_data.to_dict())
                else:
                    # Return mock data if no data exists
                    market_data.append({
                        'symbol': symbol,
                        'ltp': 0,
                        'change': 0,
                        'change_percent': 0,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            except Exception as symbol_error:
                print(f"Error getting data for {symbol}: {str(symbol_error)}")
                # Return mock data for this symbol
                market_data.append({
                    'symbol':symbol,
                    'ltp': 0,
                    'change': 0,
                    'change_percent': 0,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return jsonify(market_data), 200
        
    except Exception as e:
        print(f"Market data endpoint error: {str(e)}")
        # Return empty data instead of error
        return jsonify([]), 200

@app.route('/api/dashboard/trading-mode', methods=['GET', 'POST'])
@jwt_required()
def trading_mode():
    """Get or set trading mode (Paper/Live)"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            mode = data.get('mode', 'PAPER')
            
            # Store in session or database
            session['trading_mode'] = mode
            
            return jsonify({'mode': mode}), 200
        else:
            # Get current mode
            mode = session.get('trading_mode', 'PAPER')
            return jsonify({'mode': mode}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Volatile stocks routes
@app.route('/api/volatile-stocks', methods=['GET'])
@jwt_required()
def get_volatile_stocks():
    """Get top volatile stocks"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get top volatile stocks from database
        volatile_stocks = VolatileStock.query.order_by(
            VolatileStock.volatility_score.desc()
        ).limit(limit).all()
        
        return jsonify([stock.to_dict() for stock in volatile_stocks]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/volatile-stocks/scan', methods=['POST'])
@jwt_required()
def scan_volatile_stocks():
    """Trigger volatile stocks scan"""
    try:
        if signal_service:
            signal_service.scan_volatile_stocks()
            return jsonify({'message': 'Volatile stocks scan triggered'}), 200
        else:
            return jsonify({'error': 'Signal service not available'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Trading routes
@app.route('/api/trades', methods=['GET'])
@jwt_required()
def get_trades():
    """Get trade history"""
    try:
        # Get query parameters
        symbol = request.args.get('symbol')
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 100, type=int)
        
        # Build query
        query = Trade.query
        
        if symbol:
            query = query.filter_by(symbol=symbol)
        if status:
            query = query.filter_by(status=status)
        if date_from:
            query = query.filter(Trade.created_at >= date_from)
        if date_to:
            query = query.filter(Trade.created_at <= date_to)
        
        # Get trades
        trades = query.order_by(Trade.created_at.desc()).limit(limit).all()
        
        return jsonify([trade.to_dict() for trade in trades]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades', methods=['POST'])
@jwt_required()
def place_trade():
    """Place a new trade"""
    try:
        data = request.get_json()
        
        if not trading_service:
            return jsonify({'error': 'Trading service not available'}), 500
        
        # Validate required fields
        required_fields = ['symbol', 'trade_type', 'quantity', 'entry_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Place trade
        trade = trading_service.place_trade(
            symbol=data['symbol'],
            trade_type=data['trade_type'],
            quantity=data['quantity'],
            entry_price=data['entry_price'],
            stop_loss=data.get('stop_loss'),
            target=data.get('target'),
            trading_mode=session.get('trading_mode', 'PAPER')
        )
        
        if trade:
            return jsonify(trade.to_dict()), 201
        else:
            return jsonify({'error': 'Failed to place trade'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/<int:trade_id>/close', methods=['POST'])
@jwt_required()
def close_trade(trade_id):
    """Close a trade"""
    try:
        data = request.get_json()
        exit_price = data.get('exit_price')
        exit_reason = data.get('exit_reason', 'MANUAL')
        
        if not exit_price:
            return jsonify({'error': 'Exit price is required'}), 400
        
        if not trading_service:
            return jsonify({'error': 'Trading service not available'}), 500
        
        # Close trade
        success = trading_service.close_trade(trade_id, exit_price, exit_reason)
        
        if success:
            return jsonify({'message': 'Trade closed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to close trade'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# P&L routes
@app.route('/api/pnl/daily', methods=['GET'])
@jwt_required()
def get_daily_pnl():
    """Get daily P&L summary"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get trades for the date
        trades = Trade.query.filter(
            Trade.created_at >= f"{date} 00:00:00",
            Trade.created_at <= f"{date} 23:59:59"
        ).all()
        
        # Calculate P&L
        total_pnl = 0
        winning_trades = 0
        total_trades = len(trades)
        
        for trade in trades:
            if trade.pnl:
                total_pnl += trade.pnl
                if trade.pnl > 0:
                    winning_trades += 1
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return jsonify({
            'date': date,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'total_pnl': float(total_pnl),
            'win_rate': win_rate
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket status
@app.route('/api/websocket/status', methods=['GET'])
@jwt_required()
def websocket_status():
    """Get WebSocket connection status"""
    try:
        print(f"WebSocket client: {websocket_client}")
        if websocket_client:
            return jsonify({
                'connected': websocket_client.is_connected(),
                'subscribed_symbols': websocket_client.get_subscribed_symbols()
            }), 200
        else:
            return jsonify({'connected': False, 'subscribed_symbols': []}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'trading_service': trading_service is not None,
                'market_data_service': market_data_service is not None,
                'signal_service': signal_service is not None,
                'telegram_bot': telegram_bot is not None,
                'websocket_client': websocket_client is not None
            }
        }), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    # Initialize services
    initialize_services()
    
    # Start background tasks
    def run_background_tasks():
        """Run background tasks"""
        while True:
            try:
                with app.app_context():
                    # Update market data
                    if market_data_service:
                        market_data_service.update_market_data()
                    
                    # Scan for signals
                    if signal_service:
                        signal_service.scan_for_signals()
                    
                    # Update volatile stocks
                    if signal_service:
                        signal_service.update_volatile_stocks()
                
                # Sleep for 5 minutes (reduced frequency)
                time.sleep(300)
                
            except Exception as e:
                print(f"Background task error: {str(e)}")
                time.sleep(300)
    
    # Start background thread (disabled for now to prevent frequent updates)
    # background_thread = threading.Thread(target=run_background_tasks, daemon=True)
    # background_thread.start()
    print("Background tasks disabled to prevent frequent updates")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000) 