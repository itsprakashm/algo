import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { toast } from 'react-hot-toast';

// Components
import Login from './components/auth/Login';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';
import VolatileStocks from './components/volatile-stocks/VolatileStocks';
import TradeLogs from './components/trades/TradeLogs';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Services
import { authService } from './services/authService';
import { marketDataService } from './services/marketDataService';

// Context
import { AuthContext } from './context/AuthContext';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authService.getProfile()
        .then(userData => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  // Health check
  const { data: healthStatus } = useQuery('health', () => 
    fetch('/api/health').then(res => res.json()), {
      refetchInterval: 30000, // Check every 30 seconds
      onError: () => {
        toast.error('Backend connection lost');
      }
    }
  );

  const login = async (credentials) => {
    try {
      const response = await authService.login(credentials);
      setUser(response.user);
      localStorage.setItem('token', response.access_token);
      toast.success('Login successful');
      return response;
    } catch (error) {
      toast.error(error.message || 'Login failed');
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
    toast.success('Logged out successfully');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={
              user ? <Navigate to="/dashboard" replace /> : <Login />
            } 
          />
          <Route 
            path="/" 
            element={<Navigate to="/dashboard" replace />} 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/volatile-stocks" 
            element={
              <ProtectedRoute>
                <Layout>
                  <VolatileStocks />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/trades" 
            element={
              <ProtectedRoute>
                <Layout>
                  <TradeLogs />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="*" 
            element={<Navigate to="/dashboard" replace />} 
          />
        </Routes>
      </div>
    </AuthContext.Provider>
  );
}

export default App; 