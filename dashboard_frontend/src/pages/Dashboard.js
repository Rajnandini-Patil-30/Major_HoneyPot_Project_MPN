import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api/dashboardAPI';
import AttackMap from '../components/AttackMap';
import SessionReplay from '../components/SessionReplay';
import LiveThreatFeed from '../components/LiveThreatFeed';
import AttackTimelineChart from '../components/AttackTimelineChart';
import TopAttackersTable from '../components/TopAttackersTable';
import ProtocolBreakdown from '../components/ProtocolBreakdown';
import CredentialsTable from '../components/CredentialsTable';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [attackers, setAttackers] = useState([]);
  const [credentials, setCredentials] = useState([]);
  const [selectedPin, setSelectedPin] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      const [statsRes, attackersRes, credentialsRes] = await Promise.all([
        dashboardAPI.getStats().catch(() => ({ data: {} })),
        dashboardAPI.getAttackers(10).catch(() => ({ data: [] })),
        dashboardAPI.getCredentials(20).catch(() => ({ data: [] })),
      ]);

      setStats(statsRes.data);
      setAttackers(attackersRes.data);
      setCredentials(credentialsRes.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePinClick = (pin) => {
    setSelectedPin(pin);
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1 className="header-title">HONEYSHIELD</h1>
          <span className="header-subtitle">Threat Intelligence Platform</span>
        </div>
        <div className="header-stats">
          <div className="header-stat">
            <span className="stat-value">{stats?.total_events?.toLocaleString() || '0'}</span>
            <span className="stat-label">TOTAL EVENTS</span>
          </div>
          <div className="header-stat">
            <span className="stat-value">{stats?.unique_attackers?.toLocaleString() || '0'}</span>
            <span className="stat-label">UNIQUE IPS</span>
          </div>
          <div className="header-stat">
            <span className="stat-value">{stats?.total_sessions?.toLocaleString() || '0'}</span>
            <span className="stat-label">SESSIONS</span>
          </div>
          <div className="header-stat stat-active">
            <span className="stat-value">{stats?.events_last_24h?.toLocaleString() || '0'}</span>
            <span className="stat-label">LAST 24H</span>
          </div>
        </div>
        {loading && <div className="loading-bar"></div>}
      </header>

      {/* Main content */}
      <div className="main-content">
        {/* Map area (left) */}
        <div className="map-area">
          <AttackMap onPinClick={handlePinClick} />
          <SessionReplay
            pin={selectedPin}
            onClose={() => setSelectedPin(null)}
          />
        </div>

        {/* Right sidebar - Live Feed */}
        <div className="sidebar">
          <LiveThreatFeed />
        </div>
      </div>

      {/* Bottom panels */}
      <div className="bottom-panels">
        <div className="bottom-panel">
          <h3 className="panel-title">Protocol Distribution</h3>
          <ProtocolBreakdown />
        </div>
        <div className="bottom-panel">
          <h3 className="panel-title">Top Attackers</h3>
          {attackers.length > 0 ? (
            <TopAttackersTable attackers={attackers} />
          ) : (
            <div className="empty-state">No attack data</div>
          )}
        </div>
        <div className="bottom-panel">
          <h3 className="panel-title">Attack Timeline</h3>
          <AttackTimelineChart />
        </div>
        <div className="bottom-panel">
          <h3 className="panel-title">Captured Credentials</h3>
          {credentials.length > 0 ? (
            <CredentialsTable credentials={credentials} />
          ) : (
            <div className="empty-state">No credentials captured</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
