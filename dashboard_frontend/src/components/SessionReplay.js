import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api/dashboardAPI';
import './SessionReplay.css';

const DANGEROUS_COMMANDS = ['wget', 'curl', 'chmod', 'rm ', 'nc ', 'bash ', 'sh ', 'python', 'perl', '/etc/shadow', '/etc/passwd'];

function isDangerous(cmd) {
  return DANGEROUS_COMMANDS.some(d => cmd.toLowerCase().includes(d));
}

function SessionReplay({ pin, onClose }) {
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!pin) return;
    // Try to fetch session commands for this IP
    // We'll use the events endpoint to find a session ID for this IP
    const fetchSession = async () => {
      setLoading(true);
      try {
        // Get sessions and find one matching this IP
        await dashboardAPI.getStats();
        // For now, show pin info even without commands
        setSessionData({
          ip: pin.ip,
          country: pin.country,
          city: pin.city,
          count: pin.count,
          commands: [],
        });
      } catch (err) {
        console.error('Error fetching session:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [pin]);

  if (!pin) return null;

  return (
    <div className="session-panel">
      <div className="session-header">
        <span className="session-title">SESSION REPLAY</span>
        <span className="session-ip">
          {pin.ip} ({pin.city}, {pin.country})
        </span>
        <button className="session-close" onClick={onClose}>x</button>
      </div>
      <div className="terminal">
        {loading ? (
          <div className="terminal-loading">Loading session data...</div>
        ) : sessionData?.commands?.length > 0 ? (
          sessionData.commands.map((cmd, idx) => (
            <div key={idx} className="terminal-line">
              <span className="prompt">root@server:~$ </span>
              <span className={isDangerous(cmd.command) ? 'cmd-danger' : 'cmd-normal'}>
                {cmd.command}
              </span>
              {cmd.output && <div className="cmd-output">{cmd.output}</div>}
            </div>
          ))
        ) : (
          <>
            <div className="terminal-line">
              <span className="terminal-info">
                Attacker: {pin.ip} | Location: {pin.city}, {pin.country}
              </span>
            </div>
            <div className="terminal-line">
              <span className="terminal-info">
                Total attacks: {pin.count} | Last seen: {pin.last_seen}
              </span>
            </div>
            <div className="terminal-line">
              <span className="terminal-info terminal-dim">
                No shell commands captured for this session.
              </span>
            </div>
            <div className="terminal-line">
              <span className="prompt">root@server:~$ </span>
              <span className="cursor">_</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default SessionReplay;
