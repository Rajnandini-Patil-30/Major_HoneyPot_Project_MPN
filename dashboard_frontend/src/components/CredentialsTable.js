import React from 'react';
import './CredentialsTable.css';

function CredentialsTable({ credentials }) {
  return (
    <div className="table-wrapper">
      <table className="credentials-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Password</th>
            <th>Attempts</th>
            <th>Last Attempt</th>
          </tr>
        </thead>
        <tbody>
          {(credentials || []).slice(0, 20).map((cred, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? 'even' : 'odd'}>
              <td className="username">
                <code>{cred.username || cred.user || 'unknown'}</code>
              </td>
              <td className="password">
                <code>{'•'.repeat((cred.password || '').length)}</code>
              </td>
              <td className="attempts">
                <span className="badge">{cred.attempt_count || 1}</span>
              </td>
              <td className="time-cell">
                {cred.last_attempt ? new Date(cred.last_attempt).toLocaleTimeString() : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default CredentialsTable;
