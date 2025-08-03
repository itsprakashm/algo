-- Algo Trading Platform Database Initialization Script
-- Run this script in MySQL/XAMPP to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS algo_trading;
USE algo_trading;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    open_price DECIMAL(10,2) NOT NULL,
    high_price DECIMAL(10,2) NOT NULL,
    low_price DECIMAL(10,2) NOT NULL,
    close_price DECIMAL(10,2) NOT NULL,
    volume BIGINT,
    ltp DECIMAL(10,2),
    change DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    rsi DECIMAL(5,2),
    macd DECIMAL(10,4),
    macd_signal DECIMAL(10,4),
    macd_histogram DECIMAL(10,4),
    vwap DECIMAL(10,2),
    supertrend DECIMAL(10,2),
    supertrend_signal VARCHAR(10),
    candle_body_size DECIMAL(5,2),
    candle_wick_size DECIMAL(5,2),
    is_doji BOOLEAN DEFAULT FALSE,
    is_hammer BOOLEAN DEFAULT FALSE,
    is_shooting_star BOOLEAN DEFAULT FALSE,
    volume_sma DECIMAL(15,2),
    volume_ratio DECIMAL(5,2),
    interval VARCHAR(10) DEFAULT '1min',
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_symbol_timestamp (symbol, timestamp)
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    target_price DECIMAL(10,2),
    current_stop_loss DECIMAL(10,2),
    current_target DECIMAL(10,2),
    pnl DECIMAL(10,2),
    pnl_percentage DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'OPEN',
    trading_mode VARCHAR(10) DEFAULT 'PAPER',
    exit_reason VARCHAR(50),
    exit_time DATETIME,
    rsi_value DECIMAL(5,2),
    macd_value DECIMAL(10,4),
    macd_signal DECIMAL(10,4),
    vwap_value DECIMAL(10,2),
    supertrend_signal VARCHAR(10),
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    order_id VARCHAR(50),
    angel_order_id VARCHAR(50),
    INDEX idx_symbol (symbol),
    INDEX idx_status (status),
    INDEX idx_trading_mode (trading_mode),
    INDEX idx_created_at (created_at),
    INDEX idx_symbol_status (symbol, status)
);

-- Volatile stocks table
CREATE TABLE IF NOT EXISTS volatile_stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ltp DECIMAL(10,2) NOT NULL,
    change DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    volatility_score DECIMAL(5,2),
    price_volatility DECIMAL(5,2),
    volume_spike DECIMAL(5,2),
    candle_body_size DECIMAL(5,2),
    candle_wick_size DECIMAL(5,2),
    is_breakout BOOLEAN DEFAULT FALSE,
    is_momentum BOOLEAN DEFAULT FALSE,
    rsi DECIMAL(5,2),
    macd DECIMAL(10,4),
    macd_signal DECIMAL(10,4),
    vwap DECIMAL(10,2),
    supertrend_signal VARCHAR(10),
    signal_triggered BOOLEAN DEFAULT FALSE,
    signal_type VARCHAR(10),
    signal_strength DECIMAL(5,2),
    volume BIGINT,
    volume_sma DECIMAL(15,2),
    volume_ratio DECIMAL(5,2),
    rank INT,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_volatility_score (volatility_score),
    INDEX idx_signal_triggered (signal_triggered),
    INDEX idx_rank (rank)
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password_hash, email, is_admin) 
VALUES ('admin', 'pbkdf2:sha256:600000$your_hash_here', 'admin@algo-trading.com', TRUE)
ON DUPLICATE KEY UPDATE username=username;

-- Create indexes for better performance
CREATE INDEX idx_market_data_symbol_time ON market_data(symbol, timestamp DESC);
CREATE INDEX idx_trades_symbol_time ON trades(symbol, created_at DESC);
CREATE INDEX idx_volatile_stocks_score_time ON volatile_stocks(volatility_score DESC, timestamp DESC);

-- Create views for common queries
CREATE OR REPLACE VIEW daily_pnl_summary AS
SELECT 
    DATE(created_at) as trade_date,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl,
    (COUNT(CASE WHEN pnl > 0 THEN 1 END) / COUNT(*) * 100) as win_rate
FROM trades 
WHERE status = 'CLOSED'
GROUP BY DATE(created_at)
ORDER BY trade_date DESC;

CREATE OR REPLACE VIEW top_volatile_stocks AS
SELECT 
    symbol,
    ltp,
    change_percent,
    volatility_score,
    signal_triggered,
    signal_type,
    signal_strength,
    rank
FROM volatile_stocks 
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
ORDER BY volatility_score DESC, rank ASC;

-- Create stored procedures for common operations
DELIMITER //

CREATE PROCEDURE GetDailyPnL(IN trade_date DATE)
BEGIN
    SELECT 
        trade_date,
        COUNT(*) as total_trades,
        COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades,
        SUM(pnl) as total_pnl,
        AVG(pnl) as avg_pnl,
        (COUNT(CASE WHEN pnl > 0 THEN 1 END) / COUNT(*) * 100) as win_rate
    FROM trades 
    WHERE DATE(created_at) = trade_date AND status = 'CLOSED';
END //

CREATE PROCEDURE GetOpenTrades()
BEGIN
    SELECT * FROM trades WHERE status = 'OPEN' ORDER BY created_at DESC;
END //

CREATE PROCEDURE GetLatestMarketData(IN symbol_list TEXT)
BEGIN
    SET @sql = CONCAT('
        SELECT * FROM market_data 
        WHERE symbol IN (', symbol_list, ') 
        AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        ORDER BY symbol, timestamp DESC
    ');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON algo_trading.* TO 'your_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Show table structure
SHOW TABLES;
DESCRIBE users;
DESCRIBE market_data;
DESCRIBE trades;
DESCRIBE volatile_stocks; 