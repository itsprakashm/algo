import React from 'react';
import { TrendingUp, TrendingDown, Clock, CheckCircle, XCircle } from 'lucide-react';

const TradeLogTable = ({ trades, isLoading }) => {
  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-700 rounded mb-4"></div>
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="h-12 bg-gray-700 rounded mb-2"></div>
        ))}
      </div>
    );
  }

  if (!trades || trades.length === 0) {
    return (
      <div className="text-center py-8">
        <Clock className="h-12 w-12 mx-auto mb-4 text-gray-500" />
        <h3 className="text-lg font-medium text-gray-300 mb-2">
          No trades found
        </h3>
        <p className="text-gray-400">
          No trades match the current filters
        </p>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'OPEN':
        return <Clock className="h-4 w-4 text-warning-400" />;
      case 'CLOSED':
        return <CheckCircle className="h-4 w-4 text-success-400" />;
      case 'CANCELLED':
        return <XCircle className="h-4 w-4 text-danger-400" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'OPEN':
        return 'text-warning-400';
      case 'CLOSED':
        return 'text-success-400';
      case 'CANCELLED':
        return 'text-danger-400';
      default:
        return 'text-gray-400';
    }
  };

  const getTradeTypeColor = (type) => {
    return type === 'BUY' ? 'text-success-400' : 'text-danger-400';
  };

  const getPnLColor = (pnl) => {
    if (!pnl) return 'text-gray-400';
    return pnl > 0 ? 'text-success-400' : pnl < 0 ? 'text-danger-400' : 'text-gray-400';
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Type</th>
            <th>Quantity</th>
            <th>Entry Price</th>
            <th>Exit Price</th>
            <th>P&L</th>
            <th>Status</th>
            <th>Mode</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id}>
              <td>
                <div className="font-medium text-white">{trade.symbol}</div>
              </td>
              <td>
                <span className={`font-medium ${getTradeTypeColor(trade.trade_type)}`}>
                  {trade.trade_type}
                </span>
              </td>
              <td>
                <span className="text-gray-300">{trade.quantity}</span>
              </td>
              <td>
                <span className="text-gray-300">
                  ₹{trade.entry_price?.toFixed(2) || '0.00'}
                </span>
              </td>
              <td>
                <span className="text-gray-300">
                  {trade.exit_price ? `₹${trade.exit_price.toFixed(2)}` : '-'}
                </span>
              </td>
              <td>
                <div className="flex items-center space-x-1">
                  {trade.pnl && (
                    trade.pnl > 0 ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )
                  )}
                  <span className={`font-medium ${getPnLColor(trade.pnl)}`}>
                    {trade.pnl ? `₹${trade.pnl.toFixed(2)}` : '-'}
                  </span>
                </div>
                {trade.pnl_percentage && (
                  <div className={`text-xs ${getPnLColor(trade.pnl_percentage)}`}>
                    {trade.pnl_percentage > 0 ? '+' : ''}{trade.pnl_percentage.toFixed(2)}%
                  </div>
                )}
              </td>
              <td>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(trade.status)}
                  <span className={`font-medium ${getStatusColor(trade.status)}`}>
                    {trade.status}
                  </span>
                </div>
              </td>
              <td>
                <span className={`badge ${
                  trade.trading_mode === 'LIVE' ? 'badge-danger' : 'badge-info'
                }`}>
                  {trade.trading_mode}
                </span>
              </td>
              <td>
                <div className="text-sm text-gray-400">
                  {formatDate(trade.entry_time)}
                </div>
                {trade.exit_time && (
                  <div className="text-xs text-gray-500">
                    Exit: {formatDate(trade.exit_time)}
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TradeLogTable; 