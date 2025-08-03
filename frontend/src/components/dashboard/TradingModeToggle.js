import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { Play, Pause, AlertTriangle } from 'lucide-react';
import { marketDataService } from '../../services/marketDataService';

const TradingModeToggle = () => {
  const [isChanging, setIsChanging] = useState(false);
  const queryClient = useQueryClient();

  // Get current trading mode
  const { data: currentMode = 'PAPER' } = useQuery('trading-mode', marketDataService.getTradingMode);

  // Mutation to change trading mode
  const changeModeMutation = useMutation(
    (mode) => marketDataService.setTradingMode(mode),
    {
      onSuccess: (newMode) => {
        queryClient.setQueryData('trading-mode', newMode);
        toast.success(`Switched to ${newMode} mode`);
      },
      onError: (error) => {
        toast.error(error.message || 'Failed to change trading mode');
      },
      onSettled: () => {
        setIsChanging(false);
      }
    }
  );

  const handleModeChange = async (newMode) => {
    if (newMode === currentMode) return;
    
    setIsChanging(true);
    changeModeMutation.mutate(newMode);
  };

  const isPaperMode = currentMode === 'PAPER';
  const isLiveMode = currentMode === 'LIVE';

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Trading Mode</h3>
        {isChanging && (
          <div className="spinner w-4 h-4"></div>
        )}
      </div>

      <div className="space-y-4">
        <div className="flex items-center space-x-3">
          <div className={`flex-1 p-4 rounded-lg border-2 transition-all ${
            isPaperMode 
              ? 'border-primary-500 bg-primary-600/20' 
              : 'border-gray-600 bg-gray-700/50'
          }`}>
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${
                isPaperMode ? 'bg-primary-600' : 'bg-gray-600'
              }`}>
                <Play className="h-5 w-5 text-white" />
              </div>
              <div>
                <h4 className="font-medium text-white">Paper Trading</h4>
                <p className="text-sm text-gray-400">Practice with virtual money</p>
              </div>
            </div>
          </div>

          <button
            onClick={() => handleModeChange('PAPER')}
            disabled={isPaperMode || isChanging}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isPaperMode
                ? 'bg-primary-600 text-white cursor-default'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {isPaperMode ? 'Active' : 'Switch'}
          </button>
        </div>

        <div className="flex items-center space-x-3">
          <div className={`flex-1 p-4 rounded-lg border-2 transition-all ${
            isLiveMode 
              ? 'border-danger-500 bg-danger-600/20' 
              : 'border-gray-600 bg-gray-700/50'
          }`}>
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${
                isLiveMode ? 'bg-danger-600' : 'bg-gray-600'
              }`}>
                <AlertTriangle className="h-5 w-5 text-white" />
              </div>
              <div>
                <h4 className="font-medium text-white">Live Trading</h4>
                <p className="text-sm text-gray-400">Real money trading</p>
              </div>
            </div>
          </div>

          <button
            onClick={() => handleModeChange('LIVE')}
            disabled={isLiveMode || isChanging}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isLiveMode
                ? 'bg-danger-600 text-white cursor-default'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {isLiveMode ? 'Active' : 'Switch'}
          </button>
        </div>
      </div>

      <div className="mt-4 p-3 bg-gray-700/50 rounded-lg">
        <div className="flex items-start space-x-2">
          <AlertTriangle className="h-4 w-4 text-warning-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-gray-300">
            <p className="font-medium mb-1">Important Notice</p>
            <p className="text-xs text-gray-400">
              {isPaperMode 
                ? 'You are currently in Paper Trading mode. All trades will be simulated with virtual money.'
                : 'You are in Live Trading mode. Real money will be used for all trades. Please trade responsibly.'
              }
            </p>
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
        <div className="text-center p-2 bg-gray-700/50 rounded">
          <p className="text-gray-400">Current Mode</p>
          <p className={`font-medium ${isPaperMode ? 'text-primary-400' : 'text-danger-400'}`}>
            {currentMode}
          </p>
        </div>
        <div className="text-center p-2 bg-gray-700/50 rounded">
          <p className="text-gray-400">Status</p>
          <p className="font-medium text-success-400">
            {isChanging ? 'Changing...' : 'Active'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default TradingModeToggle; 