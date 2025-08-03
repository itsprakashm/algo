import React from 'react';
import { TrendingUp, TrendingDown, Zap, Target, Activity } from 'lucide-react';

const VolatileStockCard = ({ stock }) => {
  const {
    symbol,
    ltp,
    change_percent,
    volatility_score,
    signal_triggered,
    signal_type,
    signal_strength,
    rsi,
    macd,
    vwap,
    supertrend_signal,
    volume_ratio,
    is_breakout,
    is_momentum,
    rank
  } = stock;

  const getPriceChangeColor = (change) => {
    if (!change) return 'text-gray-400';
    return change > 0 ? 'text-success-400' : change < 0 ? 'text-danger-400' : 'text-gray-400';
  };

  const getPriceChangeIcon = (change) => {
    if (!change) return null;
    return change > 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />;
  };

  const getSignalColor = (signal) => {
    if (!signal) return 'text-gray-400';
    return signal === 'BUY' ? 'text-success-400' : 'text-danger-400';
  };

  const getVolatilityColor = (score) => {
    if (!score) return 'text-gray-400';
    if (score > 70) return 'text-danger-400';
    if (score > 50) return 'text-warning-400';
    return 'text-success-400';
  };

  const getVolatilityIcon = (score) => {
    if (!score) return null;
    if (score > 70) return <Zap className="h-4 w-4" />;
    if (score > 50) return <Target className="h-4 w-4" />;
    return <Activity className="h-4 w-4" />;
  };

  return (
    <div className="card p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-white">{symbol}</h3>
          {rank && (
            <span className="badge badge-info">#{rank}</span>
          )}
        </div>
        <div className={`flex items-center space-x-1 ${getPriceChangeColor(change_percent)}`}>
          {getPriceChangeIcon(change_percent)}
          <span className="text-sm font-medium">
            {change_percent ? `${change_percent > 0 ? '+' : ''}${change_percent.toFixed(2)}%` : '0.00%'}
          </span>
        </div>
      </div>

      {/* Price */}
      <div className="mb-4">
        <p className="text-2xl font-bold text-white">
          ₹{ltp ? ltp.toFixed(2) : '0.00'}
        </p>
      </div>

      {/* Volatility Score */}
      <div className="flex items-center justify-between mb-4 p-3 bg-gray-700/50 rounded-lg">
        <div className="flex items-center space-x-2">
          {getVolatilityIcon(volatility_score)}
          <span className="text-sm text-gray-400">Volatility</span>
        </div>
        <span className={`text-sm font-medium ${getVolatilityColor(volatility_score)}`}>
          {volatility_score?.toFixed(1) || '0.0'}
        </span>
      </div>

      {/* Signal */}
      {signal_triggered && (
        <div className="mb-4 p-3 rounded-lg border-2 border-dashed border-primary-500/50 bg-primary-600/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                signal_type === 'BUY' ? 'bg-success-400' : 'bg-danger-400'
              }`}></div>
              <span className="text-sm font-medium text-gray-300">Signal</span>
            </div>
            <span className={`text-sm font-bold ${getSignalColor(signal_type)}`}>
              {signal_type}
            </span>
          </div>
          {signal_strength && (
            <div className="mt-2">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Strength</span>
                <span>{signal_strength.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-1">
                <div 
                  className={`h-1 rounded-full ${
                    signal_strength >= 70 ? 'bg-success-500' : 
                    signal_strength >= 50 ? 'bg-warning-500' : 'bg-danger-500'
                  }`}
                  style={{ width: `${signal_strength}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Technical Indicators */}
      <div className="grid grid-cols-2 gap-3">
        {rsi && (
          <div>
            <p className="text-xs text-gray-400">RSI</p>
            <p className={`text-sm font-medium ${
              rsi < 30 ? 'text-success-400' : rsi > 70 ? 'text-danger-400' : 'text-gray-300'
            }`}>
              {rsi.toFixed(1)}
            </p>
          </div>
        )}

        {macd && (
          <div>
            <p className="text-xs text-gray-400">MACD</p>
            <p className={`text-sm font-medium ${
              macd > 0 ? 'text-success-400' : 'text-danger-400'
            }`}>
              {macd.toFixed(4)}
            </p>
          </div>
        )}

        {vwap && (
          <div>
            <p className="text-xs text-gray-400">VWAP</p>
            <p className="text-sm font-medium text-gray-300">
              ₹{vwap.toFixed(2)}
            </p>
          </div>
        )}

        {supertrend_signal && (
          <div>
            <p className="text-xs text-gray-400">Supertrend</p>
            <p className={`text-sm font-medium ${getSignalColor(supertrend_signal)}`}>
              {supertrend_signal}
            </p>
          </div>
        )}
      </div>

      {/* Volume and Patterns */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-2 gap-3">
          {volume_ratio && (
            <div>
              <p className="text-xs text-gray-400">Volume Ratio</p>
              <p className={`text-sm font-medium ${
                volume_ratio > 1.5 ? 'text-success-400' : 
                volume_ratio > 1.2 ? 'text-warning-400' : 'text-gray-300'
              }`}>
                {volume_ratio.toFixed(2)}x
              </p>
            </div>
          )}

          <div>
            <p className="text-xs text-gray-400">Patterns</p>
            <div className="flex space-x-1">
              {is_breakout && (
                <span className="badge badge-success text-xs">Breakout</span>
              )}
              {is_momentum && (
                <span className="badge badge-warning text-xs">Momentum</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Action Button */}
      {signal_triggered && (
        <div className="mt-4">
          <button className={`w-full btn ${
            signal_type === 'BUY' ? 'btn-success' : 'btn-danger'
          }`}>
            {signal_type === 'BUY' ? 'Buy Now' : 'Sell Now'}
          </button>
        </div>
      )}
    </div>
  );
};

export default VolatileStockCard; 