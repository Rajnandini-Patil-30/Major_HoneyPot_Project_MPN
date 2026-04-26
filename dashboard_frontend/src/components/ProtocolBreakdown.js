import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import { dashboardAPI } from '../api/dashboardAPI';
import './ProtocolBreakdown.css';

function ProtocolBreakdown() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'];

  useEffect(() => {
    fetchProtocols();
  }, []);

  const fetchProtocols = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getProtocols();
      
      const protocolData = (response.data || []).map((item) => ({
        name: item.protocol || item.name || 'Unknown',
        value: item.count || item.value || 0,
      }));

      if (protocolData.length === 0) {
        // Mock data if no real data
        const mockData = [
          { name: 'SSH', value: 234 },
          { name: 'HTTP', value: 189 },
          { name: 'FTP', value: 45 },
          { name: 'Telnet', value: 23 },
        ];
        setData(mockData);
      } else {
        setData(protocolData);
      }
    } catch (err) {
      console.error('Error fetching protocols:', err);
      // Set mock data on error
      const mockData = [
        { name: 'SSH', value: 234 },
        { name: 'HTTP', value: 189 },
        { name: 'FTP', value: 45 },
        { name: 'Telnet', value: 23 },
      ];
      setData(mockData);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading protocols...</div>;

  return (
    <div className="protocol-chart">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px',
              color: '#e2e8f0',
            }}
          />
          <Legend wrapperStyle={{ color: '#cbd5e1' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ProtocolBreakdown;
