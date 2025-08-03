import pandas as pd
import numpy as np
from typing import List, Tuple, Optional

def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: List of closing prices
        period: RSI period (default: 14)
    
    Returns:
        RSI value or None if insufficient data
    """
    if len(prices) < period + 1:
        return None
    
    prices = np.array(prices)
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gains and losses
    avg_gains = np.mean(gains[:period])
    avg_losses = np.mean(losses[:period])
    
    for i in range(period, len(deltas)):
        avg_gains = (avg_gains * (period - 1) + gains[i]) / period
        avg_losses = (avg_losses * (period - 1) + losses[i]) / period
    
    if avg_losses == 0:
        return 100
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)

def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: List of closing prices
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
    
    Returns:
        Tuple of (MACD, Signal, Histogram) or (None, None, None) if insufficient data
    """
    if len(prices) < slow_period + signal_period:
        return None, None, None
    
    prices = np.array(prices)
    
    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)
    
    if ema_fast is None or ema_slow is None:
        return None, None, None
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line (EMA of MACD)
    macd_values = []
    for i in range(len(prices) - slow_period + 1):
        ema_fast_i = calculate_ema(prices[i:i+slow_period], fast_period)
        ema_slow_i = calculate_ema(prices[i:i+slow_period], slow_period)
        if ema_fast_i is not None and ema_slow_i is not None:
            macd_values.append(ema_fast_i - ema_slow_i)
    
    if len(macd_values) < signal_period:
        return float(macd_line), None, None
    
    signal_line = calculate_ema(macd_values, signal_period)
    histogram = macd_line - signal_line if signal_line is not None else None
    
    return float(macd_line), float(signal_line) if signal_line is not None else None, float(histogram) if histogram is not None else None

def calculate_ema(prices: np.ndarray, period: int) -> Optional[float]:
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    alpha = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = alpha * price + (1 - alpha) * ema
    
    return ema

def calculate_vwap(prices: List[float], volumes: List[int], period: int = 20) -> Optional[float]:
    """
    Calculate Volume Weighted Average Price (VWAP)
    
    Args:
        prices: List of prices (typically typical price: (H+L+C)/3)
        volumes: List of volumes
        period: VWAP period
    
    Returns:
        VWAP value or None if insufficient data
    """
    if len(prices) < period or len(volumes) < period:
        return None
    
    # Use last 'period' data points
    recent_prices = prices[-period:]
    recent_volumes = volumes[-period:]
    
    # Calculate typical price if not already calculated
    if len(recent_prices) == period:
        typical_prices = recent_prices
    else:
        typical_prices = recent_prices
    
    # Calculate VWAP
    volume_price_sum = sum(p * v for p, v in zip(typical_prices, recent_volumes))
    total_volume = sum(recent_volumes)
    
    if total_volume == 0:
        return None
    
    vwap = volume_price_sum / total_volume
    return float(vwap)

def calculate_supertrend(highs: List[float], lows: List[float], closes: List[float], 
                        period: int = 10, multiplier: float = 3.0) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculate Supertrend indicator
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of close prices
        period: ATR period
        multiplier: ATR multiplier
    
    Returns:
        Tuple of (Supertrend value, Signal) or (None, None) if insufficient data
    """
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None, None
    
    # Calculate ATR
    atr = calculate_atr(highs, lows, closes, period)
    if atr is None:
        return None, None
    
    # Calculate basic upper and lower bands
    basic_upper = (highs[-1] + lows[-1]) / 2 + (multiplier * atr)
    basic_lower = (highs[-1] + lows[-1]) / 2 - (multiplier * atr)
    
    # Calculate final upper and lower bands
    final_upper = basic_upper
    final_lower = basic_lower
    
    # Adjust bands based on previous values
    if len(highs) > 1:
        prev_final_upper = final_upper  # This would be the previous final upper
        prev_final_lower = final_lower  # This would be the previous final lower
        
        if basic_upper < prev_final_upper or closes[-2] > prev_final_upper:
            final_upper = basic_upper
        else:
            final_upper = prev_final_upper
        
        if basic_lower > prev_final_lower or closes[-2] < prev_final_lower:
            final_lower = basic_lower
        else:
            final_lower = prev_final_lower
    
    # Determine signal
    current_close = closes[-1]
    signal = None
    
    if current_close > final_upper:
        signal = "BUY"
    elif current_close < final_lower:
        signal = "SELL"
    else:
        # Maintain previous signal
        signal = "HOLD"  # This would need to be tracked from previous calculations
    
    return float(final_upper if signal == "BUY" else final_lower), signal

def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
    """Calculate Average True Range (ATR)"""
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None
    
    true_ranges = []
    for i in range(1, len(closes)):
        high_low = highs[i] - lows[i]
        high_close = abs(highs[i] - closes[i-1])
        low_close = abs(lows[i] - closes[i-1])
        true_range = max(high_low, high_close, low_close)
        true_ranges.append(true_range)
    
    if len(true_ranges) < period:
        return None
    
    # Calculate ATR using simple moving average
    atr = sum(true_ranges[-period:]) / period
    return float(atr)

def calculate_volume_sma(volumes: List[int], period: int = 20) -> Optional[float]:
    """Calculate Simple Moving Average of volume"""
    if len(volumes) < period:
        return None
    
    recent_volumes = volumes[-period:]
    sma = sum(recent_volumes) / period
    return float(sma)

def calculate_volume_ratio(current_volume: int, volume_sma: float) -> Optional[float]:
    """Calculate volume ratio (current volume / average volume)"""
    if volume_sma is None or volume_sma == 0:
        return None
    
    ratio = current_volume / volume_sma
    return float(ratio)

def calculate_price_volatility(prices: List[float], period: int = 20) -> Optional[float]:
    """Calculate price volatility as percentage"""
    if len(prices) < period:
        return None
    
    recent_prices = prices[-period:]
    returns = []
    
    for i in range(1, len(recent_prices)):
        if recent_prices[i-1] != 0:
            return_val = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
            returns.append(return_val)
    
    if not returns:
        return None
    
    volatility = np.std(returns) * 100  # Convert to percentage
    return float(volatility) 