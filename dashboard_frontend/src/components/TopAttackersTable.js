import React from 'react';
import './TopAttackersTable.css';

function TopAttackersTable({ attackers }) {
  return (
    <div className="table-wrapper">
      <table className="attackers-table">
        <thead>
          <tr>
            <th>Attacker IP</th>
            <th>Attack Count</th>
            <th>Country</th>
            <th>Port</th>
            <th>Last Seen</th>
          </tr>
        </thead>
        <tbody>
          {(attackers || []).map((attacker, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? 'even' : 'odd'}>
              <td className="ip-cell">
                <code>{attacker.ip || attacker.attacker_ip || 'Unknown'}</code>
              </td>
              <td className="count-cell">
                <span className="badge">{attacker.attack_count || attacker.count || 0}</span>
              </td>
              <td>{attacker.country || attacker.location || 'Unknown'}</td>
              <td>{attacker.port || attacker.source_port || '-'}</td>
              <td className="time-cell">
                {attacker.last_seen  ? new Date(attacker.last_seen).toLocaleTimeString() : 'Unknown'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TopAttackersTable;
