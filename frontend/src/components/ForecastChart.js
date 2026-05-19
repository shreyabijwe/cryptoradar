import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function ForecastChart({ token, API }) {
  const [data, setData] = useState([]);
  const [coin, setCoin] = useState('bitcoin');
  const [loading, setLoading] = useState(false);

  const coins = ['bitcoin'];

  // eslint-disable-next-line
  useEffect(() => {
    setLoading(true);
    fetch(`${API}/forecast/${coin}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(result => {
        if (result.forecast_inr) {
          const chartData = result.forecast_inr.map((price, i) => ({
            day: `Day ${i + 1}`,
            price_inr: price
          }));
          setData(chartData);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [coin]);

  return (
    <div style={styles.card}>
      <h3 style={styles.title}>► LSTM 7-DAY FORECAST (BTC/INR)</h3>
      {loading ? (
        <p style={{ color: '#334155', fontFamily: 'Courier New', fontSize: 12 }}>COMPUTING FORECAST...</p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(30,58,110,0.3)" />
            <XAxis dataKey="day" tick={{ fill: '#334155', fontSize: 10, fontFamily: 'Courier New' }} />
            <YAxis tick={{ fill: '#334155', fontSize: 10 }}
              tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`} />
            <Tooltip
              formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, 'Forecast']}
              contentStyle={{ background: '#0d1b33', border: '1px solid #60a5fa8', fontFamily: 'Courier New', fontSize: 11 }}
              labelStyle={{ color: '#60a5fa' }}
            />
            <Line type="monotone" dataKey="price_inr" stroke="#38bdf8"
              strokeWidth={2} dot={{ fill: '#38bdf8', r: 4 }} strokeDasharray="5 5" />
          </LineChart>
        </ResponsiveContainer>
      )}
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
};

export default ForecastChart;