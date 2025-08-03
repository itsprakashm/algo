#!/usr/bin/env python3
"""
Script to initialize market data in the database
"""

from app import app, db
from models.market_data import MarketData
from datetime import datetime, timedelta
import random

def init_market_data():
    """Initialize market data with sample data"""
    try:
        with app.app_context():
            # Check if market data already exists
            existing_data = MarketData.query.first()
            if existing_data:
                print("Market data already exists, skipping initialization")
                return
            
            print("Initializing market data...")
            
            # Sample data for the last 24 hours
            symbols = ["NIFTY", "BANKNIFTY", "SENSEX"]
            base_prices = {
                "NIFTY": 19000,
                "BANKNIFTY": 44000,
                "SENSEX": 65000
            }
            
            # Generate data for the last 24 hours (every 5 minutes)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            current_time = start_time
            while current_time <= end_time:
                for symbol in symbols:
                    base_price = base_prices[symbol]
                    
                    # Generate realistic price movements
                    price_change = random.uniform(-2, 2)  # -2% to +2%
                    open_price = base_price * (1 + price_change / 100)
                    high_price = open_price * (1 + random.uniform(0, 0.5) / 100)
                    low_price = open_price * (1 - random.uniform(0, 0.5) / 100)
                    close_price = open_price * (1 + random.uniform(-0.3, 0.3) / 100)
                    
                    # Ensure high >= open,close and low <= open,close
                    high_price = max(high_price, open_price, close_price)
                    low_price = min(low_price, open_price, close_price)
                    
                    volume = random.randint(1000000, 10000000)
                    change = close_price - open_price
                    change_percent = (change / open_price) * 100 if open_price > 0 else 0
                    
                    # Create market data record
                    market_data = MarketData(
                        symbol=symbol,
                        open_price=open_price,
                        high_price=high_price,
                        low_price=low_price,
                        close_price=close_price,
                        volume=volume,
                        ltp=close_price,
                        change=change,
                        change_percent=change_percent,
                        timestamp=current_time
                    )
                    
                    # Calculate candle analysis
                    market_data.calculate_candle_analysis()
                    
                    db.session.add(market_data)
                
                # Move to next 5-minute interval
                current_time += timedelta(minutes=5)
            
            # Commit all data
            db.session.commit()
            print("Market data initialized successfully!")
            
    except Exception as e:
        print(f"Error initializing market data: {str(e)}")

if __name__ == "__main__":
    init_market_data() 