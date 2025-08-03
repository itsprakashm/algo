import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  TrendingUp, 
  TrendingDown, 
  Filter, 
  Download,
  Calendar,
  DollarSign,
  Activity
} from 'lucide-react';
import { marketDataService } from '../../services/marketDataService';
import TradeLogTable from './TradeLogTable';
import TradeFilters from './TradeFilters';

const TradeLogs = () => {
  const [filters, setFilters] = useState({
    symbol: '',
    status: '',
    date_from: '',
    date_to: '',
    limit: 100
  });

  // Fetch trades with filters
  const { 
    data: trades, 
    isLoading, 
    error, 
    refetch 
  } = useQuery(['trades', filters], () => marketDataService.getTrades(filters), {
    refetchInterval: 30000, // Refresh every 30 seconds
    refetchOnWindowFocus: false,
  });

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const handleRefresh = () => {
    refetch();
    toast.success('Trade logs refreshed');
  };

  // Calculate summary statistics
  const calculateStats = () => {
    if (!trades) return {};
    
    const totalTrades = trades.length;
    const openTrades = trades.filter(t => t.status === 'OPEN').length;
    const closedTrades = trades.filter(t => t.status === 'CLOSED').length;
    const totalPnL = trades.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const winningTrades = trades.filter(t => t.pnl && t.pnl > 0).length;
    const losingTrades = trades.filter(t => t.pnl && t.pnl < 0).length;
    const winRate = closedTrades > 0 ? (winningTrades / closedTrades) * 100 : 0;

    return {
      totalTrades,
      openTrades,
      closedTrades,
      totalPnL,
      winningTrades,
      losingTrades,
      winRate
    };
  };

  const stats = calculateStats();

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-danger-400 mb-4">
          <Activity className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-300 mb-2">
          Failed to load trade logs
        </h3>
        <p className="text-gray-400 mb-4">
          {error.message || 'Please check your connection and try again'}
        </p>
        <button onClick={handleRefresh} className="btn-primary">
          <Activity className="h-4 w-4 mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Trade Logs</h1>
          <p className="text-gray-400">Complete history of all trades and performance</p>
        </div>
        
        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="btn-secondary flex items-center space-x-2"
          >
            <Activity className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-primary-600 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total Trades</p>
              <p className="text-lg font-semibold text-white">
                {stats.totalTrades}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-success-600 rounded-lg">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Open Trades</p>
              <p className="text-lg font-semibold text-white">
                {stats.openTrades}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-warning-600 rounded-lg">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total P&L</p>
              <p className={`text-lg font-semibold ${
                stats.totalPnL > 0 ? 'text-success-400' : 
                stats.totalPnL < 0 ? 'text-danger-400' : 'text-white'
              }`}>
                ₹{stats.totalPnL.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-success-600 rounded-lg">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Win Rate</p>
              <p className="text-lg font-semibold text-white">
                {stats.winRate.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <TradeFilters 
        filters={filters} 
        onFilterChange={handleFilterChange} 
      />

      {/* Trade Table */}
      <div className="card">
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Trade History</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">
              {trades?.length || 0} trades
            </span>
            <button className="btn-secondary flex items-center space-x-2">
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>
        <div className="p-6">
          <TradeLogTable 
            trades={trades} 
            isLoading={isLoading} 
          />
        </div>
      </div>

      {/* Performance Summary */}
      {stats.closedTrades > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Performance Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Closed Trades</span>
                <span className="text-white font-medium">{stats.closedTrades}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Winning Trades</span>
                <span className="text-success-400 font-medium">{stats.winningTrades}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Losing Trades</span>
                <span className="text-danger-400 font-medium">{stats.losingTrades}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Win Rate</span>
                <span className="text-white font-medium">{stats.winRate.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">P&L Analysis</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Total P&L</span>
                <span className={`font-medium ${
                  stats.totalPnL > 0 ? 'text-success-400' : 
                  stats.totalPnL < 0 ? 'text-danger-400' : 'text-white'
                }`}>
                  ₹{stats.totalPnL.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Average P&L per Trade</span>
                <span className={`font-medium ${
                  stats.totalPnL > 0 ? 'text-success-400' : 
                  stats.totalPnL < 0 ? 'text-danger-400' : 'text-white'
                }`}>
                  ₹{(stats.totalPnL / stats.closedTrades).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Best Trade</span>
                <span className="text-success-400 font-medium">
                  ₹{Math.max(...(trades?.map(t => t.pnl || 0) || [0]))}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Worst Trade</span>
                <span className="text-danger-400 font-medium">
                  ₹{Math.min(...(trades?.map(t => t.pnl || 0) || [0]))}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradeLogs; 