# Algo Trading Platform - Setup Guide

## 🚀 Quick Start

This guide will help you set up the complete algo trading platform for scalping.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - Backend runtime
- **Node.js 16+** - Frontend runtime
- **XAMPP** - MySQL database server
- **Git** - Version control

### Required Accounts
- **Angel One Trading Account** - For API access
- **Telegram Bot** - For alerts (optional but recommended)

## 🔧 Installation Steps

### 1. Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd algo-trading-platform

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Database Setup

1. **Start XAMPP**
   - Open XAMPP Control Panel
   - Start Apache and MySQL services

2. **Create Database**
   ```sql
   -- Open phpMyAdmin (http://localhost/phpmyadmin)
   -- Create new database: algo_trading
   -- Import the database/init.sql file
   ```

### 3. Environment Configuration

1. **Create .env file**
   ```bash
   cp .env.example .env
   ```

2. **Configure Angel One API**
   - Get your API credentials from Angel One
   - Update the following in `.env`:
     ```
     API_KEY=your_angel_one_api_key
     CLIENT_ID=your_angel_one_client_id
     TOTP_SECRET=your_angel_one_totp_secret
     CLIENT_PIN=your_angel_one_client_pin
     ```

3. **Configure Telegram Bot (Optional)**
   - Create a bot via @BotFather on Telegram
   - Get your chat ID
   - Update in `.env`:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token
     TELEGRAM_CHAT_ID=your_chat_id
     ```

4. **Configure Database**
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=algo_trading
   ```

### 4. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

The backend will start on `http://localhost:5000`

### 5. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will start on `http://localhost:3000`

## 🔐 Initial Login

1. Open `http://localhost:3000` in your browser
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

## 📊 Platform Features

### Dashboard
- Real-time market data for NIFTY, BANKNIFTY, SENSEX
- Configurable candle intervals (1min, 3min, 5min)
- Paper/Live trading mode toggle
- Daily P&L summary

### Volatile Stocks Scanner
- Top 5-10 volatile stocks detection
- Real-time volume and price analysis
- Telegram alerts for trade setups
- Manual trade execution buttons

### Trade Management
- Complete trade history with filters
- Paper and Live trading modes
- Stop loss and target management
- P&L tracking and analysis

### Signal Logic
- RSI, MACD, VWAP, Supertrend indicators
- Scalping-optimized entry conditions
- Breakout momentum detection
- Volume-based confirmation

## ⚙️ Configuration Options

### Trading Parameters
```env
# Risk Management
DEFAULT_RISK_REWARD_RATIO=1.5
TRAILING_STOP_PERCENTAGE=0.5
MAX_DAILY_LOSS=1000
MAX_POSITION_SIZE=10000

# Technical Indicators
RSI_PERIOD=14
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9
SUPERTREND_PERIOD=10
SUPERTREND_MULTIPLIER=3.0
VWAP_PERIOD=20
```

### Signal Conditions
- **Primary BUY**: RSI < 30 + Supertrend BUY + VWAP support
- **Exception BUY**: RSI > 30 but other indicators align + strong breakout
- **Volume Filter**: Ignored for Index instruments
- **Breakout Detection**: Momentum candles with volume spike

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure XAMPP MySQL is running
   - Check database credentials in `.env`
   - Verify database `algo_trading` exists

2. **Angel One API Error**
   - Verify API credentials in `.env`
   - Check if TOTP secret is correct
   - Ensure account has API access enabled

3. **WebSocket Connection Issues**
   - Check Angel One API login
   - Verify network connectivity
   - Check firewall settings

4. **Frontend Not Loading**
   - Ensure backend is running on port 5000
   - Check if all dependencies are installed
   - Clear browser cache

### Logs and Debugging

- **Backend Logs**: Check console output when running `python app.py`
- **Frontend Logs**: Check browser developer console
- **Database Logs**: Check XAMPP MySQL logs

## 🚨 Important Notes

### Security
- Change default admin password after first login
- Use strong passwords for production
- Keep API credentials secure
- Enable HTTPS in production

### Trading Risks
- Always test in Paper mode first
- Start with small position sizes
- Monitor trades actively
- Set appropriate stop losses

### Performance
- Monitor system resources
- Check database performance
- Optimize WebSocket connections
- Regular backup of trade data

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all prerequisites are met
4. Verify configuration settings

## ⚠️ Disclaimer

This platform is for educational purposes. Trading involves risk. Always test thoroughly in paper mode before live trading. The developers are not responsible for any financial losses. 