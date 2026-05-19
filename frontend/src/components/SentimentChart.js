import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function SentimentChart({ token, API }) {
  const [data, setData] = useState([]);

  // eslint-disable-next-line
  useEffect(() => {
    fetch(`${API}/sentiment`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setData(data))
      .catch(() => {});
  }, []);

  return (
    <div style={styles.card}>
      <h3 style={styles.title}>► MARKET SENTIMENT</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(30,58,110,0.3)" />
          <XAxis dataKey="coin_id" tick={{ fill: '#334155', fontSize: 10, fontFamily: 'Courier New' }}
            tickFormatter={(v) => v === 'bitcoin' ? 'BTC' : v === 'ethereum' ? 'ETH' : v === 'binancecoin' ? 'BNB' : 'SOL'} />
          <YAxis tick={{ fill: '#334155', fontSize: 10 }} />
          <Tooltip
            formatter={(value, name) => [value, name]}
            contentStyle={{ background: '#0d1b33', border: '1px solid #60a5fa', fontFamily: 'Courier New', fontSize: 11 }}
            labelStyle={{ color: '#60a5fa' }}
          />
          <Bar dataKey="positive" name="Positive" fill="#60a5fa" radius={[2, 2, 0, 0]} />
          <Bar dataKey="negative" name="Negative" fill="#ff4444" radius={[2, 2, 0, 0]} />
          <Bar dataKey="neutral"  name="Neutral"  fill="#334155" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <div style={styles.summary}>
        {data.map((d, i) => (
          <div key={i} style={styles.summaryItem}>
            <span style={styles.coinLabel}>
              {d.coin_id === 'bitcoin' ? 'BTC' : d.coin_id === 'ethereum' ? 'ETH' : d.coin_id === 'binancecoin' ? 'BNB' : 'SOL'}
            </span>
            <span style={{
              ...styles.signal,
              color: d.overall === 'BULLISH' ? '#00ff88' : d.overall === 'BEARISH' ? '#ff4444' : '#004422'
            }}>
              {d.overall}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: '#0d1b33',
    border: '1px solid #1e3a6e',
    borderRadius: '4px',
    padding: '16px',
  },
  title: {
    fontSize: '12px',
    color: '#60a5fa',
    fontFamily: 'Courier New',
    letterSpacing: '1px',
    marginBottom: '12px',
  },
  summary: {
    display: 'flex',
    justifyContent: 'space-around',
    marginTop: '12px',
  },
  summaryItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
  },
  coinLabel: {
    fontSize: '10px',
    color: '#334155',
    fontFamily: 'Courier New',
  },
  signal: {
    fontSize: '10px',
    fontFamily: 'Courier New',
    letterSpacing: '1px',
  },
};

export default SentimentChart;