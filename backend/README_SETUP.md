# Algo Trading Backend Setup Guide

## Prerequisites

1. Python 3.8 or higher
2. MySQL database
3. Angel One trading account and API credentials

## Installation

1. **Clone the repository and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `env.example` to `.env`
   - Update the credentials in `.env` file

## Configuration

### 1. Database Setup

Create a MySQL database named `algo_trading` and update the database credentials in `.env`:

```env
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=algo_trading
```

### 2. Angel One API Credentials

You need to get the following credentials from Angel One:

1. **API Key**: Get from Angel One developer portal
2. **Client ID**: Your Angel One client ID
3. **TOTP Secret**: Secret key for generating TOTP
4. **Client PIN**: Your trading account PIN

Update these in your `.env` file:

```env
API_KEY=your_actual_api_key
CLIENT_ID=your_actual_client_id
TOTP_SECRET=your_actual_totp_secret
CLIENT_PIN=your_actual_client_pin
```

### 3. Default Admin Credentials

The application creates a default admin user. You can customize these credentials:

```env
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASSWORD=admin123
```

## Running the Application

1. **Initialize the database**
   ```bash
   python app.py
   ```

2. **Start the Flask server**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Dashboard
- `GET /api/dashboard/market-data` - Get market data
- `GET /api/dashboard/trading-mode` - Get/set trading mode

### Volatile Stocks
- `GET /api/volatile-stocks` - Get volatile stocks
- `POST /api/volatile-stocks/scan` - Scan for volatile stocks

### Trades
- `GET /api/trades` - Get trade history
- `POST /api/trades` - Place new trade
- `POST /api/trades/<id>/close` - Close trade

### P&L
- `GET /api/pnl/daily` - Get daily P&L

## Troubleshooting

### WebSocket Connection Issues

If you encounter WebSocket authentication errors:

1. **Check Angel One credentials**: Ensure all credentials are correct and not expired
2. **Verify API permissions**: Make sure your Angel One account has WebSocket access
3. **Check token validity**: The access token expires every 24 hours
4. **Feed token issues**: The feed token might be different from the access token

### Common Error Messages

- `401 Unauthorized`: Invalid or expired credentials
- `Authentication Failed`: Check API key, client ID, and tokens
- `Feed Token expired`: Re-login to get fresh tokens

## Security Notes

1. **Never commit `.env` file**: It contains sensitive credentials
2. **Use strong passwords**: Change default admin password
3. **Regular token refresh**: Access tokens expire every 24 hours
4. **Paper trading mode**: Enable for testing without real money

## Support

For issues related to:
- **Angel One API**: Contact Angel One support
- **Application**: Check logs in the console output
- **Database**: Verify MySQL connection and permissions 