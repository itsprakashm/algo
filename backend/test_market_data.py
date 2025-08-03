#!/usr/bin/env python3
"""
Test script to verify market data availability
"""

from app import app, db
from models.market_data import MarketData
from datetime import datetime, timedelta

def test_market_data():
    """Test market data availability"""
    try:
        with app.app_context():
            # Check if market data exists
            total_records = MarketData.query.count()
            print(f"Total market data records: {total_records}")
            
            # Get latest data for each symbol
            symbols = ["NIFTY", "BANKNIFTY", "SENSEX"]
            
            for symbol in symbols:
                latest_data = MarketData.query.filter_by(symbol=symbol).order_by(
                    MarketData.timestamp.desc()
                ).first()
                
                if latest_data:
                    print(f"\n{symbol}:")
                    print(f"  LTP: {latest_data.ltp}")
                    print(f"  Change: {latest_data.change}")
                    print(f"  Change %: {latest_data.change_percent}")
                    print(f"  Timestamp: {latest_data.timestamp}")
                else:
                    print(f"\n{symbol}: No data found")
            
            # Check data from last 24 hours
            yesterday = datetime.utcnow() - timedelta(hours=24)
            recent_data = MarketData.query.filter(
                MarketData.timestamp >= yesterday
            ).count()
            
            print(f"\nRecords from last 24 hours: {recent_data}")
            
    except Exception as e:
        print(f"Error testing market data: {str(e)}")

if __name__ == "__main__":
    test_market_data() 