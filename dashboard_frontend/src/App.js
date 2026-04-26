import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard';
import { dashboardAPI } from './api/dashboardAPI';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check API connection
    checkApiConnection();
    const interval = setInterval(checkApiConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkApiConnection = async () => {
    try {
      await dashboardAPI.healthCheck();
      setIsConnected(true);
    } catch (error) {
      console.error('API Connection Failed:', error);
      setIsConnected(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app loading">
        <div className="spinner"></div>
        <p>Initializing Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {!isConnected && (
        <div className="connection-warning">
          API Backend Connection Failed - Ensure backend is running on 195.250.20.9:5000
        </div>
      )}
      <Dashboard />
    </div>
  );
}

export default App;
