# Algo Trading Platform

A complete algorithmic trading platform built with Angel One SmartAPI, MySQL, and React + Tailwind CSS for scalping strategies.

## 🚀 Features

### 🔐 Authentication
- Secure login with JWT-based authentication
- Environment-based credentials management
- Protected API endpoints

### 📊 Real-Time Dashboard
- Live price feeds for NIFTY, BANKNIFTY, and SENSEX
- Configurable candle intervals (1min, 3min, 5min)
- Paper/Live trading mode toggle

### 🔍 Volatile Stocks Scanner
- Top 5-10 volatile stocks detection
- Real-time volume and price analysis
- Telegram alerts for trade setups

### 📈 Advanced Signal Logic
- RSI, MACD, VWAP, Supertrend indicators
- Scalping-optimized entry conditions
- Breakout momentum detection

### 🤖 Trade Engine
- Paper and Live trading modes
- Angel One SmartAPI integration
- Automated order placement
- Telegram notifications

### 📉 P&L Management
- Dynamic target extension
- Stop loss trailing
- Partial exit handling
- Day-end P&L calculation

## 🛠️ Tech Stack

- **Frontend**: React + Tailwind CSS
- **Backend**: Python Flask
- **Database**: MySQL (XAMPP)
- **Real-time Data**: Angel One WebSocket Streaming 2.0
- **Alerts**: Telegram Bot API
- **Charts**: Recharts/TradingView

## 📁 Project Structure

```
algo-trading-platform/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration management
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── public/             # Static files
│   ├── src/                # React components
│   ├── package.json        # Node dependencies
│   └── tailwind.config.js  # Tailwind configuration
├── database/               # Database scripts
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🚀 Quick Start

1. **Clone the repository**
2. **Set up environment variables** (copy `backend/env.example` to `backend/.env`)
3. **Install dependencies**
4. **Start XAMPP MySQL**
5. **Run backend**: `cd backend && python app.py`
6. **Run frontend**: `cd frontend && npm start`

### Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

## 📋 Environment Variables

Create a `.env` file with the following variables:

```env
# Angel One API Credentials
API_KEY=your_api_key
CLIENT_ID=your_client_id
TOTP_SECRET=your_totp_secret
CLIENT_PIN=your_client_pin

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=algo_trading

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Admin Credentials
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASSWORD=admin123
```

## 🔧 Installation

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Database Setup
1. Start XAMPP and MySQL
2. Create database: `algo_trading`
3. Run database scripts in `database/` folder

## 📊 Usage

1. **Login** with admin credentials
2. **Configure** trading parameters
3. **Monitor** real-time data on dashboard
4. **Scan** volatile stocks for opportunities
5. **Execute** trades in paper/live mode
6. **Track** P&L and performance

## 🔧 Troubleshooting

### WebSocket Connection Issues
If you encounter WebSocket authentication errors:

1. **Check Angel One credentials**: Ensure all credentials are correct and not expired
2. **Verify API permissions**: Make sure your Angel One account has WebSocket access
3. **Check token validity**: The access token expires every 24 hours
4. **Test connection**: Run `python test_websocket.py` to test your credentials

### Common Error Messages
- `401 Unauthorized`: Invalid or expired credentials
- `Authentication Failed`: Check API key, client ID, and tokens
- `Feed Token expired`: Re-login to get fresh tokens

### Testing Your Setup
Run the test script to verify your configuration:
```bash
cd backend
python test_websocket.py
```

## 📚 Documentation
- **Backend Setup**: See `backend/README_SETUP.md` for detailed backend configuration
- **API Documentation**: Check the Flask routes in `backend/app.py`

## ⚠️ Disclaimer

This platform is for educational purposes. Trading involves risk. Always test thoroughly in paper mode before live trading.

## 📄 License

MIT License - see LICENSE file for details. 


