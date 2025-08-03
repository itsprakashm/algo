import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  RefreshCw,
  Play,
  Pause
} from 'lucide-react';
import { marketDataService } from '../../services/marketDataService';
import MarketDataCard from './MarketDataCard';
import TradingModeToggle from './TradingModeToggle';
import DailyPnL from './DailyPnL';
import MarketChart from './MarketChart';

const Dashboard = () => {
  const [selectedInterval, setSelectedInterval] = useState('1min');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch market data
  const { 
    data: marketData, 
    isLoading, 
    error, 
    refetch 
  } = useQuery('market-data', () => marketDataService.getMarketData(), {
    refetchInterval: autoRefresh ? 30000 : false, // Refresh every 30 seconds if auto-refresh is on
    refetchOnWindowFocus: false,
  });

  // Fetch daily P&L
  const { data: dailyPnL } = useQuery('daily-pnl', () => marketDataService.getDailyPnL(), {
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const handleRefresh = () => {
    refetch();
    toast.success('Market data refreshed');
  };

  const getPriceChangeColor = (change) => {
    if (!change) return 'text-gray-400';
    return change > 0 ? 'text-success-400' : change < 0 ? 'text-danger-400' : 'text-gray-400';
  };

  const getPriceChangeIcon = (change) => {
    if (!change) return null;
    return change > 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />;
  };

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-danger-400 mb-4">
          <Activity className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-300 mb-2">
          Failed to load market data
        </h3>
        <p className="text-gray-400 mb-4">
          {error.message || 'Please check your connection and try again'}
        </p>
        <button onClick={handleRefresh} className="btn-primary">
          <RefreshCw className="h-4 w-4 mr-2" />
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
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400">Real-time market overview and trading insights</p>
        </div>
        
        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          {/* Auto-refresh toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              autoRefresh 
                ? 'bg-success-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {autoRefresh ? (
              <>
                <Play className="h-4 w-4" />
                Auto-refresh ON
              </>
            ) : (
              <>
                <Pause className="h-4 w-4" />
                Auto-refresh OFF
              </>
            )}
          </button>

          {/* Manual refresh */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Market Data Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {marketData?.map((data) => (
          <MarketDataCard
            key={data.symbol}
            data={data}
            isLoading={isLoading}
          />
        ))}
      </div>

      {/* Trading Mode and P&L */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TradingModeToggle />
        <DailyPnL data={dailyPnL} />
      </div>

      {/* Market Chart */}
      <div className="card">
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Market Overview</h2>
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-400">Interval:</label>
            <select
              value={selectedInterval}
              onChange={(e) => setSelectedInterval(e.target.value)}
              className="select text-sm"
            >
              <option value="1min">1 Min</option>
              <option value="3min">3 Min</option>
              <option value="5min">5 Min</option>
            </select>
          </div>
        </div>
        <div className="p-6">
          <MarketChart interval={selectedInterval} />
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-primary-600 rounded-lg">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total P&L</p>
              <p className="text-lg font-semibold text-white">
                ₹{dailyPnL?.total_pnl?.toFixed(2) || '0.00'}
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
                {dailyPnL?.win_rate?.toFixed(1) || '0.0'}%
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-warning-600 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total Trades</p>
              <p className="text-lg font-semibold text-white">
                {dailyPnL?.total_trades || 0}
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
              <p className="text-sm font-medium text-gray-400">Winning Trades</p>
              <p className="text-lg font-semibold text-white">
                {dailyPnL?.winning_trades || 0}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 