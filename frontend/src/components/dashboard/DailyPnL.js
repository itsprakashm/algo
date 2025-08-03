import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';

const DailyPnL = ({ data }) => {
  if (!data) {
    return (
      <div className="card p-6">
        <div className="text-center text-gray-400">
          <Activity className="h-8 w-8 mx-auto mb-2" />
          <p>No P&L data available</p>
        </div>
      </div>
    );
  }

  const {
    date,
    total_trades,
    winning_trades,
    total_pnl,
    win_rate
  } = data;

  const isProfitable = total_pnl > 0;
  const hasTrades = total_trades > 0;

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Daily P&L</h3>
        <div className="text-sm text-gray-400">
          {date}
        </div>
      </div>

      <div className="space-y-4">
        {/* Total P&L */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <DollarSign className="h-6 w-6 text-gray-400" />
            <span className="text-sm text-gray-400">Total P&L</span>
          </div>
          <div className={`text-3xl font-bold ${
            isProfitable ? 'text-success-400' : total_pnl < 0 ? 'text-danger-400' : 'text-gray-300'
          }`}>
            ₹{total_pnl?.toFixed(2) || '0.00'}
          </div>
          {hasTrades && (
            <div className={`flex items-center justify-center space-x-1 mt-1 ${
              isProfitable ? 'text-success-400' : total_pnl < 0 ? 'text-danger-400' : 'text-gray-400'
            }`}>
              {isProfitable ? (
                <TrendingUp className="h-4 w-4" />
              ) : total_pnl < 0 ? (
                <TrendingDown className="h-4 w-4" />
              ) : null}
              <span className="text-sm">
                {isProfitable ? 'Profitable' : total_pnl < 0 ? 'Loss' : 'Neutral'}
              </span>
            </div>
          )}
        </div>

        {/* Trade Statistics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-gray-700/50 rounded-lg">
            <div className="text-2xl font-bold text-white">
              {total_trades || 0}
            </div>
            <div className="text-xs text-gray-400">Total Trades</div>
          </div>

          <div className="text-center p-3 bg-gray-700/50 rounded-lg">
            <div className="text-2xl font-bold text-success-400">
              {winning_trades || 0}
            </div>
            <div className="text-xs text-gray-400">Winning Trades</div>
          </div>
        </div>

        {/* Win Rate */}
        <div className="text-center p-3 bg-gray-700/50 rounded-lg">
          <div className="text-2xl font-bold text-white">
            {win_rate?.toFixed(1) || '0.0'}%
          </div>
          <div className="text-xs text-gray-400">Win Rate</div>
        </div>

        {/* Performance Bar */}
        {hasTrades && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-gray-400">
              <span>Win Rate</span>
              <span>{win_rate?.toFixed(1) || '0.0'}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all ${
                  win_rate >= 60 ? 'bg-success-500' : win_rate >= 40 ? 'bg-warning-500' : 'bg-danger-500'
                }`}
                style={{ width: `${Math.min(win_rate || 0, 100)}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Summary */}
        {hasTrades && (
          <div className="mt-4 p-3 bg-gray-700/50 rounded-lg">
            <div className="text-sm text-gray-300">
              <p className="mb-1">
                <span className="font-medium">Summary:</span>
              </p>
              <ul className="text-xs text-gray-400 space-y-1">
                <li>• {total_trades} trades executed today</li>
                <li>• {winning_trades} profitable trades</li>
                <li>• {total_trades - winning_trades} losing trades</li>
                <li>• Average P&L per trade: ₹{(total_pnl / total_trades).toFixed(2)}</li>
              </ul>
            </div>
          </div>
        )}

        {/* No Trades Message */}
        {!hasTrades && (
          <div className="text-center py-4">
            <Activity className="h-8 w-8 mx-auto mb-2 text-gray-500" />
            <p className="text-sm text-gray-400">No trades executed today</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DailyPnL; 