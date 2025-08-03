import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  RefreshCw, 
  AlertTriangle,
  Play,
  Target,
  Zap
} from 'lucide-react';
import { marketDataService } from '../../services/marketDataService';
import VolatileStockCard from './VolatileStockCard';

const VolatileStocks = () => {
  const [autoRefresh, setAutoRefresh] = useState(true);
  const queryClient = useQueryClient();

  // Fetch volatile stocks
  const { 
    data: volatileStocks, 
    isLoading, 
    error, 
    refetch 
  } = useQuery('volatile-stocks', () => marketDataService.getVolatileStocks(10), {
    refetchInterval: autoRefresh ? 30000 : false, // Refresh every 30 seconds if auto-refresh is on
    refetchOnWindowFocus: false,
  });

  // Scan mutation
  const scanMutation = useMutation(
    () => marketDataService.scanVolatileStocks(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('volatile-stocks');
        toast.success('Volatile stocks scan completed');
      },
      onError: (error) => {
        toast.error(error.message || 'Failed to scan volatile stocks');
      }
    }
  );

  const handleScan = () => {
    scanMutation.mutate();
  };

  const handleRefresh = () => {
    refetch();
    toast.success('Volatile stocks refreshed');
  };

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-danger-400 mb-4">
          <Activity className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-300 mb-2">
          Failed to load volatile stocks
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
          <h1 className="text-2xl font-bold text-white">Volatile Stocks</h1>
          <p className="text-gray-400">Top volatile stocks with trading signals</p>
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
                <Activity className="h-4 w-4" />
                Auto-refresh OFF
              </>
            )}
          </button>

          {/* Manual scan */}
          <button
            onClick={handleScan}
            disabled={scanMutation.isLoading}
            className="btn-warning flex items-center space-x-2"
          >
            <Zap className={`h-4 w-4 ${scanMutation.isLoading ? 'animate-spin' : ''}`} />
            {scanMutation.isLoading ? 'Scanning...' : 'Scan Now'}
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

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-primary-600 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total Stocks</p>
              <p className="text-lg font-semibold text-white">
                {volatileStocks?.length || 0}
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
              <p className="text-sm font-medium text-gray-400">Buy Signals</p>
              <p className="text-lg font-semibold text-white">
                {volatileStocks?.filter(stock => stock.signal_type === 'BUY').length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-danger-600 rounded-lg">
              <TrendingDown className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Sell Signals</p>
              <p className="text-lg font-semibold text-white">
                {volatileStocks?.filter(stock => stock.signal_type === 'SELL').length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-warning-600 rounded-lg">
              <Target className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">High Volatility</p>
              <p className="text-lg font-semibold text-white">
                {volatileStocks?.filter(stock => stock.volatility_score > 50).length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Volatile Stocks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          // Loading skeletons
          Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="card p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-700 rounded w-1/2 mb-4"></div>
                <div className="h-8 bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-700 rounded w-1/2 mb-4"></div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="h-3 bg-gray-700 rounded"></div>
                  <div className="h-3 bg-gray-700 rounded"></div>
                </div>
              </div>
            </div>
          ))
        ) : volatileStocks?.length > 0 ? (
          volatileStocks.map((stock) => (
            <VolatileStockCard key={stock.id} stock={stock} />
          ))
        ) : (
          <div className="col-span-full text-center py-8">
            <Activity className="h-12 w-12 mx-auto mb-4 text-gray-500" />
            <h3 className="text-lg font-medium text-gray-300 mb-2">
              No volatile stocks found
            </h3>
            <p className="text-gray-400 mb-4">
              Run a scan to find volatile stocks with trading opportunities
            </p>
            <button onClick={handleScan} className="btn-primary">
              <Zap className="h-4 w-4 mr-2" />
              Scan for Volatile Stocks
            </button>
          </div>
        )}
      </div>

      {/* Information Panel */}
      <div className="card p-6">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-warning-400 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-gray-300 mb-2">
              About Volatile Stocks Scanner
            </h3>
            <div className="text-sm text-gray-400 space-y-2">
              <p>
                The volatile stocks scanner identifies stocks with high price volatility, 
                volume spikes, and technical indicator alignments that may present trading opportunities.
              </p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Analyzes price volatility, volume spikes, and technical indicators</li>
                <li>Generates BUY/SELL signals based on RSI, MACD, VWAP, and Supertrend</li>
                <li>Sends Telegram alerts for high-probability setups</li>
                <li>Updates automatically every 30 seconds</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VolatileStocks; 