import React, { useState, useEffect, useCallback } from 'react';
import { dashboardAPI } from '../api/dashboardAPI';
import './LiveThreatFeed.css';

const PROTOCOL_CLASSES = {
  SSH: 'proto-ssh',
  HTTP: 'proto-http',
  FTP: 'proto-ftp',
  Telnet: 'proto-telnet',
};

function timeAgo(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const seconds = Math.floor((now - then) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

function LiveThreatFeed() {
  const [events, setEvents] = useState([]);

  const fetchEvents = useCallback(async () => {
    try {
      const res = await dashboardAPI.getRecentEvents(20);
      setEvents(res.data || []);
    } catch (err) {
      console.error('Error fetching recent events:', err);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 5000);
    return () => clearInterval(interval);
  }, [fetchEvents]);

  return (
    <div className="live-feed">
      <div className="feed-title">
        <span className="feed-dot"></span>
        LIVE THREAT FEED
      </div>
      <div className="feed-list">
        {events.map((evt) => (
          <div key={evt.id} className="feed-item">
            <span className={`proto-badge ${PROTOCOL_CLASSES[evt.protocol] || 'proto-ssh'}`}>
              {evt.protocol === 'Telnet' ? 'TEL' : evt.protocol}
            </span>
            <span className="feed-detail">
              {evt.detail || `${evt.protocol} from ${evt.ip}`}
              {evt.ip && <span className="feed-ip"> from {evt.ip}</span>}
            </span>
            <span className="feed-time">{timeAgo(evt.timestamp)}</span>
          </div>
        ))}
        {events.length === 0 && (
          <div className="feed-empty">Waiting for attack events...</div>
        )}
      </div>
    </div>
  );
}

export default LiveThreatFeed;
