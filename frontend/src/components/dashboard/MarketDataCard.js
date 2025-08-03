import React from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

const MarketDataCard = ({ data, isLoading }) => {
  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-700 rounded w-1/2 mb-4"></div>
          <div className="h-8 bg-gray-700 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card p-6">
        <div className="text-center text-gray-400">
          <Activity className="h-8 w-8 mx-auto mb-2" />
          <p>No data available</p>
        </div>
      </div>
    );
  }

  const {
    symbol,
    ltp,
    change,
    change_percent,
    rsi,
    macd,
    vwap,
    supertrend_signal
  } = data;

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

  return (
    <div className="card p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{symbol}</h3>
        <div className={`flex items-center space-x-1 ${getPriceChangeColor(change)}`}>
          {getPriceChangeIcon(change)}
          <span className="text-sm font-medium">
            {change_percent ? `${change_percent > 0 ? '+' : ''}${change_percent.toFixed(2)}%` : '0.00%'}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-2xl font-bold text-white">
            ₹{ltp ? ltp.toFixed(2) : '0.00'}
          </p>
          {change && (
            <p className={`text-sm ${getPriceChangeColor(change)}`}>
              {change > 0 ? '+' : ''}{change.toFixed(2)}
            </p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
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
      </div>
    </div>
  );
};

export default MarketDataCard; 