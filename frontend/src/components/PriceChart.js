import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function PriceChart({ token, API }) {
  const [data, setData] = useState([]);
  const [coin, setCoin] = useState('bitcoin');

  const coins = ['bitcoin', 'ethereum', 'binancecoin', 'solana'];

  // eslint-disable-next-line
  useEffect(() => {
    fetch(`${API}/historical/${coin}?days=30`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setData(data))
      .catch(() => {});
  }, [coin]);

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>► PRICE CHART (30D)</h3>
        <div style={styles.tabs}>
          {coins.map(c => (
            <button
              key={c}
              onClick={() => setCoin(c)}
              style={{
                ...styles.tab,
                color: coin === c ? '#60a5fa' : '#004422',
                borderColor: coin === c ? '#60a5fa' : '#004422',
              }}
            >
              {c === 'bitcoin' ? 'BTC' : c === 'ethereum' ? 'ETH' : c === 'binancecoin' ? 'BNB' : 'SOL'}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(30,58,110,0.3)" />
          <XAxis dataKey="date" tick={{ fill: '#334155', fontSize: 10, fontFamily: 'Courier New' }}
            tickFormatter={(v) => v.slice(5)} />
          <YAxis tick={{ fill: '#334155', fontSize: 10, fontFamily: 'Courier New' }}
            tickFormatter={(v) => `₹${(v/1000).toFixed(0)}K`} />
          <Tooltip
            formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, 'Price']}
            contentStyle={{ background: '', border: '1px solid #60a5fa', fontFamily: 'Courier New', fontSize: 11 }}
            labelStyle={{ color: '#60a5fa' }}
          />
          <Line type="monotone" dataKey="price_inr" stroke="#60a5fa" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  title: {
    fontSize: '12px',
    color: '#60a5fa',
    fontFamily: 'Courier New',
    letterSpacing: '1px',
  },
  tabs: {
    display: 'flex',
    gap: '6px',
  },
  tab: {
    padding: '3px 8px',
    background: 'transparent',
    border: '1px solid',
    borderRadius: '2px',
    cursor: 'pointer',
    fontSize: '10px',
    fontFamily: 'Courier New',
    letterSpacing: '1px',
  },
};

export default PriceChart;