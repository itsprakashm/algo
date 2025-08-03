from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from models.market_data import MarketData
from utils.technical_indicators import *

class MarketDataService:
    """Service for handling market data operations"""
    
    def __init__(self, db):
        self.db = db
        self.cache = {}  # Simple cache for market data
    
    def handle_ltp_update(self, symbol: str, data: Dict[str, Any]):
        """Handle LTP (Last Traded Price) update from WebSocket"""
        try:
            ltp = data.get('ltp')
            change = data.get('change', 0)
            change_percent = data.get('change_percent', 0)
            timestamp = data.get('timestamp')
            
            if ltp:
                # Update cache
                self.cache[symbol] = {
                    'ltp': ltp,
                    'change': change,
                    'change_percent': change_percent,
                    'timestamp': timestamp
                }
                
                # Store in database
                market_data = MarketData(
                    symbol=symbol,
                    open_price=ltp,  # Simplified for LTP updates
                    high_price=ltp,
                    low_price=ltp,
                    close_price=ltp,
                    ltp=ltp,
                    change=change,
                    change_percent=change_percent
                )
                
                self.db.session.add(market_data)
                self.db.session.commit()
                
        except Exception as e:
            print(f"Handle LTP update error: {str(e)}")
    
    def handle_ohlc_update(self, symbol: str, data: Dict[str, Any]):
        """Handle OHLC update from WebSocket"""
        try:
            open_price = data.get('open')
            high_price = data.get('high')
            low_price = data.get('low')
            close_price = data.get('close')
            volume = data.get('volume')
            timestamp = data.get('timestamp')
            
            if all([open_price, high_price, low_price, close_price]):
                # Calculate technical indicators
                indicators = self._calculate_indicators(symbol, open_price, high_price, low_price, close_price, volume)
                
                # Create market data record
                market_data = MarketData(
                    symbol=symbol,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume,
                    **indicators
                )
                
                # Calculate candle analysis
                market_data.calculate_candle_analysis()
                
                self.db.session.add(market_data)
                self.db.session.commit()
                
        except Exception as e:
            print(f"Handle OHLC update error: {str(e)}")
    
    def _calculate_indicators(self, symbol: str, open_price: float, high_price: float, 
                            low_price: float, close_price: float, volume: int = None) -> Dict[str, Any]:
        """Calculate technical indicators for market data"""
        try:
            indicators = {}
            
            # Get historical data for calculations
            historical_data = self._get_historical_data(symbol, 50)
            
            if historical_data:
                closes = [d.close_price for d in historical_data]
                highs = [d.high_price for d in historical_data]
                lows = [d.low_price for d in historical_data]
                volumes = [d.volume for d in historical_data if d.volume]
                
                # Calculate RSI
                rsi = calculate_rsi(closes)
                if rsi:
                    indicators['rsi'] = rsi
                
                # Calculate MACD
                macd, macd_signal, macd_histogram = calculate_macd(closes)
                if macd:
                    indicators['macd'] = macd
                if macd_signal:
                    indicators['macd_signal'] = macd_signal
                if macd_histogram:
                    indicators['macd_histogram'] = macd_histogram
                
                # Calculate VWAP
                if volumes and len(volumes) >= 20:
                    typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
                    vwap = calculate_vwap(typical_prices, volumes)
                    if vwap:
                        indicators['vwap'] = vwap
                
                # Calculate Supertrend
                supertrend, supertrend_signal = calculate_supertrend(highs, lows, closes)
                if supertrend:
                    indicators['supertrend'] = supertrend
                if supertrend_signal:
                    indicators['supertrend_signal'] = supertrend_signal
                
                # Calculate volume indicators
                if volumes:
                    volume_sma = calculate_volume_sma(volumes)
                    if volume_sma and volume:
                        volume_ratio = calculate_volume_ratio(volume, volume_sma)
                        if volume_ratio:
                            indicators['volume_ratio'] = volume_ratio
                        indicators['volume_sma'] = volume_sma
                
                # Calculate price volatility
                price_volatility = calculate_price_volatility(closes)
                if price_volatility:
                    indicators['price_volatility'] = price_volatility
            
            return indicators
            
        except Exception as e:
            print(f"Calculate indicators error: {str(e)}")
            return {}
    
    def _get_historical_data(self, symbol: str, limit: int = 50) -> List[MarketData]:
        """Get historical market data for symbol"""
        try:
            return MarketData.query.filter_by(symbol=symbol).order_by(
                MarketData.timestamp.desc()
            ).limit(limit).all()
        except Exception as e:
            print(f"Get historical data error: {str(e)}")
            return []
    
    def get_latest_market_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get latest market data for symbols"""
        try:
            market_data = []
            
            for symbol in symbols:
                # Check cache first
                if symbol in self.cache:
                    cache_data = self.cache[symbol]
                    market_data.append({
                        'symbol': symbol,
                        **cache_data
                    })
                else:
                    # Get from database
                    latest = MarketData.query.filter_by(symbol=symbol).order_by(
                        MarketData.timestamp.desc()
                    ).first()
                    
                    if latest:
                        market_data.append(latest.to_dict())
            
            return market_data
            
        except Exception as e:
            print(f"Get latest market data error: {str(e)}")
            return []
    
    def update_market_data(self):
        """Update market data (called by background task)"""
        try:
            # This would typically fetch data from external APIs
            # For now, we'll just process any pending data
            
            # Get symbols that need updates
            symbols = ["NIFTY", "BANKNIFTY", "SENSEX"]
            
            for symbol in symbols:
                # Check if we have recent data
                latest = MarketData.query.filter_by(symbol=symbol).order_by(
                    MarketData.timestamp.desc()
                ).first()
                
                if not latest or (datetime.utcnow() - latest.timestamp).seconds > 60:
                    # Need to fetch new data
                    self._fetch_market_data(symbol)
                    
        except Exception as e:
            print(f"Update market data error: {str(e)}")
    
    def _fetch_market_data(self, symbol: str):
        """Fetch market data for symbol (placeholder)"""
        try:
            # This would integrate with Angel One API or other data providers
            # For now, we'll create mock data
            
            import random
            
            base_price = {
                "NIFTY": 19000,
                "BANKNIFTY": 44000,
                "SENSEX": 65000
            }.get(symbol, 100)
            
            # Generate mock data
            open_price = base_price + random.uniform(-100, 100)
            high_price = open_price + random.uniform(0, 50)
            low_price = open_price - random.uniform(0, 50)
            close_price = open_price + random.uniform(-30, 30)
            volume = random.randint(1000000, 10000000)
            
            # Create market data record
            market_data = MarketData(
                symbol=symbol,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                ltp=close_price,
                change=close_price - open_price,
                change_percent=((close_price - open_price) / open_price) * 100
            )
            
            # Calculate indicators
            indicators = self._calculate_indicators(symbol, open_price, high_price, low_price, close_price, volume)
            for key, value in indicators.items():
                setattr(market_data, key, value)
            
            # Calculate candle analysis
            market_data.calculate_candle_analysis()
            
            self.db.session.add(market_data)
            self.db.session.commit()
            
        except Exception as e:
            print(f"Fetch market data error: {str(e)}")
    
    def get_market_data_history(self, symbol: str, interval: str = '1min', 
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical market data for symbol"""
        try:
            query = MarketData.query.filter_by(symbol=symbol, interval=interval)
            
            if interval == '1min':
                # Get last 100 records
                data = query.order_by(MarketData.timestamp.desc()).limit(limit).all()
            elif interval == '5min':
                # Get every 5th record
                data = query.order_by(MarketData.timestamp.desc()).limit(limit * 5).all()
                data = data[::5]  # Take every 5th record
            else:
                data = query.order_by(MarketData.timestamp.desc()).limit(limit).all()
            
            return [record.to_dict() for record in data]
            
        except Exception as e:
            print(f"Get market data history error: {str(e)}")
            return []
    
    def get_top_gainers_losers(self, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Get top gainers and losers"""
        try:
            # Get latest data for all symbols
            all_symbols = self.db.session.query(MarketData.symbol).distinct().all()
            symbols = [s[0] for s in all_symbols]
            
            gainers = []
            losers = []
            
            for symbol in symbols:
                latest = MarketData.query.filter_by(symbol=symbol).order_by(
                    MarketData.timestamp.desc()
                ).first()
                
                if latest and latest.change_percent:
                    data = latest.to_dict()
                    if latest.change_percent > 0:
                        gainers.append(data)
                    else:
                        losers.append(data)
            
            # Sort by change percentage
            gainers.sort(key=lambda x: x['change_percent'], reverse=True)
            losers.sort(key=lambda x: x['change_percent'])
            
            return {
                'gainers': gainers[:limit],
                'losers': losers[:limit]
            }
            
        except Exception as e:
            print(f"Get top gainers losers error: {str(e)}")
            return {'gainers': [], 'losers': []} 