import { api } from './authService';

export const marketDataService = {
  async getMarketData(symbols = ['NIFTY', 'BANKNIFTY', 'SENSEX']) {
    try {
      const response = await api.get('/dashboard/market-data', {
        params: { symbols }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch market data');
    }
  },

  async getTradingMode() {
    try {
      const response = await api.get('/dashboard/trading-mode');
      return response.data.mode;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get trading mode');
    }
  },

  async setTradingMode(mode) {
    try {
      const response = await api.post('/dashboard/trading-mode', { mode });
      return response.data.mode;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to set trading mode');
    }
  },

  async getVolatileStocks(limit = 10) {
    try {
      const response = await api.get('/volatile-stocks', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch volatile stocks');
    }
  },

  async scanVolatileStocks() {
    try {
      const response = await api.post('/volatile-stocks/scan');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to scan volatile stocks');
    }
  },

  async getTrades(filters = {}) {
    try {
      const response = await api.get('/trades', { params: filters });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch trades');
    }
  },

  async placeTrade(tradeData) {
    try {
      const response = await api.post('/trades', tradeData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to place trade');
    }
  },

  async closeTrade(tradeId, exitData) {
    try {
      const response = await api.post(`/trades/${tradeId}/close`, exitData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to close trade');
    }
  },

  async getDailyPnL(date = null) {
    try {
      const response = await api.get('/pnl/daily', {
        params: { date }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch daily P&L');
    }
  },

  async getWebSocketStatus() {
    try {
      const response = await api.get('/websocket/status');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get WebSocket status');
    }
  },
}; 