from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from models.market_data import MarketData
from models.volatile_stock import VolatileStock
from models.trade import Trade
from utils.technical_indicators import *
from utils.telegram_bot import TelegramBot

class SignalService:
    """Service for generating trading signals and managing volatile stocks"""
    
    def __init__(self, db, telegram_bot: TelegramBot):
        self.db = db
        self.telegram_bot = telegram_bot
        self.signal_cache = {}  # Cache for signals to avoid duplicates
    
    def scan_for_signals(self):
        """Scan for trading signals across all symbols"""
        try:
            # Get all symbols with recent data
            symbols = self.db.session.query(MarketData.symbol).distinct().all()
            symbols = [s[0] for s in symbols]
            
            for symbol in symbols:
                self._check_signal_for_symbol(symbol)
                
        except Exception as e:
            print(f"Scan for signals error: {str(e)}")
            if self.telegram_bot:
                self.telegram_bot.send_error_alert(str(e), "SignalService")
    
    def _check_signal_for_symbol(self, symbol: str):
        """Check for trading signals for a specific symbol"""
        try:
            # Get latest market data
            latest_data = MarketData.query.filter_by(symbol=symbol).order_by(
                MarketData.timestamp.desc()
            ).first()
            
            if not latest_data:
                return
            
            # Get historical data for indicators
            historical_data = self._get_historical_data(symbol, 50)
            if not historical_data:
                return
            
            # Calculate indicators
            indicators = self._calculate_indicators(historical_data)
            
            # Check for signal conditions
            signal = self._check_signal_conditions(symbol, latest_data, indicators)
            
            if signal:
                # Check if signal is new (not in cache)
                signal_key = f"{symbol}_{signal['type']}_{datetime.now().strftime('%Y%m%d%H%M')}"
                
                if signal_key not in self.signal_cache:
                    self.signal_cache[signal_key] = True
                    
                    # Send Telegram alert
                    if self.telegram_bot:
                        self.telegram_bot.send_trade_signal(
                            symbol=symbol,
                            signal_type=signal['type'],
                            price=float(latest_data.close_price),
                            indicators=indicators,
                            reason=signal['reason']
                        )
                    
                    print(f"Signal generated for {symbol}: {signal['type']} - {signal['reason']}")
                    
        except Exception as e:
            print(f"Check signal for symbol error: {str(e)}")
    
    def _calculate_indicators(self, historical_data: List[MarketData]) -> Dict[str, Any]:
        """Calculate technical indicators from historical data"""
        try:
            indicators = {}
            
            if len(historical_data) < 20:
                return indicators
            
            # Extract price data
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
            
            return indicators
            
        except Exception as e:
            print(f"Calculate indicators error: {str(e)}")
            return {}
    
    def _check_signal_conditions(self, symbol: str, latest_data: MarketData, 
                                indicators: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for signal conditions based on indicators"""
        try:
            signal = None
            
            # Primary BUY conditions: RSI < 30 + Supertrend BUY + VWAP support
            if (indicators.get('rsi') and indicators['rsi'] < 30 and
                indicators.get('supertrend_signal') == 'BUY' and
                indicators.get('vwap') and latest_data.close_price > indicators['vwap']):
                
                signal = {
                    'type': 'BUY',
                    'reason': 'RSI oversold + Supertrend BUY + VWAP support',
                    'strength': 85
                }
            
            # Exception: Allow BUY if RSI > 30 but other indicators align and strong breakout
            elif (indicators.get('rsi') and indicators['rsi'] > 30 and indicators['rsi'] < 60 and
                  indicators.get('supertrend_signal') == 'BUY' and
                  latest_data.is_breakout and latest_data.volume_ratio and latest_data.volume_ratio > 1.5):
                
                signal = {
                    'type': 'BUY',
                    'reason': 'Strong breakout + Supertrend BUY + Volume spike',
                    'strength': 75
                }
            
            # SELL conditions: RSI > 70 + Supertrend SELL + VWAP resistance
            elif (indicators.get('rsi') and indicators['rsi'] > 70 and
                  indicators.get('supertrend_signal') == 'SELL' and
                  indicators.get('vwap') and latest_data.close_price < indicators['vwap']):
                
                signal = {
                    'type': 'SELL',
                    'reason': 'RSI overbought + Supertrend SELL + VWAP resistance',
                    'strength': 85
                }
            
            # MACD crossover signals
            elif (indicators.get('macd') and indicators.get('macd_signal') and
                  indicators['macd'] > indicators['macd_signal'] and
                  indicators.get('supertrend_signal') == 'BUY'):
                
                signal = {
                    'type': 'BUY',
                    'reason': 'MACD bullish crossover + Supertrend BUY',
                    'strength': 70
                }
            
            elif (indicators.get('macd') and indicators.get('macd_signal') and
                  indicators['macd'] < indicators['macd_signal'] and
                  indicators.get('supertrend_signal') == 'SELL'):
                
                signal = {
                    'type': 'SELL',
                    'reason': 'MACD bearish crossover + Supertrend SELL',
                    'strength': 70
                }
            
            return signal
            
        except Exception as e:
            print(f"Check signal conditions error: {str(e)}")
            return None
    
    def scan_volatile_stocks(self):
        """Scan for volatile stocks"""
        try:
            # Get all symbols with recent data
            symbols = self.db.session.query(MarketData.symbol).distinct().all()
            symbols = [s[0] for s in symbols]
            
            volatile_stocks = []
            
            for symbol in symbols:
                # Skip index instruments
                if symbol in ["NIFTY", "BANKNIFTY", "SENSEX"]:
                    continue
                
                volatile_stock = self._analyze_volatility(symbol)
                if volatile_stock:
                    volatile_stocks.append(volatile_stock)
            
            # Sort by volatility score and take top stocks
            volatile_stocks.sort(key=lambda x: x.volatility_score or 0, reverse=True)
            top_volatile = volatile_stocks[:10]
            
            # Update database
            for i, stock in enumerate(top_volatile):
                stock.rank = i + 1
                self.db.session.add(stock)
            
            self.db.session.commit()
            
            # Send alerts for high volatility stocks
            for stock in top_volatile[:5]:
                if stock.signal_triggered and self.telegram_bot:
                    self.telegram_bot.send_volatile_stock_alert(
                        symbol=stock.symbol,
                        ltp=float(stock.ltp),
                        change_percent=float(stock.change_percent) if stock.change_percent else 0,
                        volatility_score=float(stock.volatility_score) if stock.volatility_score else 0,
                        signal_triggered=True
                    )
                    
        except Exception as e:
            print(f"Scan volatile stocks error: {str(e)}")
            if self.telegram_bot:
                self.telegram_bot.send_error_alert(str(e), "SignalService")
    
    def _analyze_volatility(self, symbol: str) -> Optional[VolatileStock]:
        """Analyze volatility for a symbol"""
        try:
            # Get latest market data
            latest_data = MarketData.query.filter_by(symbol=symbol).order_by(
                MarketData.timestamp.desc()
            ).first()
            
            if not latest_data:
                return None
            
            # Get historical data
            historical_data = self._get_historical_data(symbol, 20)
            if len(historical_data) < 10:
                return None
            
            # Calculate volatility metrics
            closes = [d.close_price for d in historical_data]
            volumes = [d.volume for d in historical_data if d.volume]
            
            # Calculate price volatility
            price_volatility = calculate_price_volatility(closes)
            
            # Calculate volume spike
            volume_spike = None
            if volumes and len(volumes) >= 10:
                current_volume = volumes[-1]
                avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
                if avg_volume > 0:
                    volume_spike = current_volume / avg_volume
            
            # Calculate indicators
            indicators = self._calculate_indicators(historical_data)
            
            # Create volatile stock record
            volatile_stock = VolatileStock(
                symbol=symbol,
                ltp=latest_data.close_price,
                change=latest_data.change,
                change_percent=latest_data.change_percent,
                price_volatility=price_volatility,
                volume_spike=volume_spike,
                candle_body_size=latest_data.candle_body_size,
                candle_wick_size=latest_data.candle_wick_size,
                volume=latest_data.volume,
                volume_sma=latest_data.volume_sma,
                volume_ratio=latest_data.volume_ratio,
                **indicators
            )
            
            # Calculate volatility score
            volatile_stock.calculate_volatility_score()
            
            # Check for breakout patterns
            if len(historical_data) > 1:
                volatile_stock.check_breakout_pattern(historical_data[-2])
            
            # Generate signal
            volatile_stock.generate_signal()
            
            return volatile_stock
            
        except Exception as e:
            print(f"Analyze volatility error: {str(e)}")
            return None
    
    def _get_historical_data(self, symbol: str, limit: int = 50) -> List[MarketData]:
        """Get historical market data for symbol"""
        try:
            return MarketData.query.filter_by(symbol=symbol).order_by(
                MarketData.timestamp.desc()
            ).limit(limit).all()
        except Exception as e:
            print(f"Get historical data error: {str(e)}")
            return []
    
    def update_volatile_stocks(self):
        """Update volatile stocks (called by background task)"""
        try:
            # Remove old volatile stock records (older than 1 hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            VolatileStock.query.filter(VolatileStock.timestamp < cutoff_time).delete()
            self.db.session.commit()
            
            # Scan for new volatile stocks
            self.scan_volatile_stocks()
            
        except Exception as e:
            print(f"Update volatile stocks error: {str(e)}")
    
    def get_signal_history(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get signal history for a symbol"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get market data with signals
            market_data = MarketData.query.filter(
                MarketData.symbol == symbol,
                MarketData.timestamp >= cutoff_date
            ).order_by(MarketData.timestamp.desc()).all()
            
            signals = []
            for data in market_data:
                # Check if this data point had a signal
                indicators = {
                    'rsi': data.rsi,
                    'macd': data.macd,
                    'macd_signal': data.macd_signal,
                    'vwap': data.vwap,
                    'supertrend_signal': data.supertrend_signal
                }
                
                signal = self._check_signal_conditions(symbol, data, indicators)
                if signal:
                    signals.append({
                        'timestamp': data.timestamp.isoformat(),
                        'price': float(data.close_price),
                        'signal': signal
                    })
            
            return signals
            
        except Exception as e:
            print(f"Get signal history error: {str(e)}")
            return []
    
    def get_signal_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get signal statistics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all signals in the period
            all_signals = []
            symbols = self.db.session.query(MarketData.symbol).distinct().all()
            
            for symbol in symbols:
                symbol_signals = self.get_signal_history(symbol[0], days)
                all_signals.extend(symbol_signals)
            
            # Calculate statistics
            total_signals = len(all_signals)
            buy_signals = len([s for s in all_signals if s['signal']['type'] == 'BUY'])
            sell_signals = len([s for s in all_signals if s['signal']['type'] == 'SELL'])
            
            return {
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'buy_percentage': (buy_signals / total_signals * 100) if total_signals > 0 else 0,
                'sell_percentage': (sell_signals / total_signals * 100) if total_signals > 0 else 0
            }
            
        except Exception as e:
            print(f"Get signal statistics error: {str(e)}")
            return {
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'buy_percentage': 0,
                'sell_percentage': 0
            } 