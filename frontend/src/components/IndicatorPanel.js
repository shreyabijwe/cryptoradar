import React, { useState, useEffect } from 'react';

function IndicatorPanel({ token, API }) {
  const [data, setData] = useState(null);
  const [coin, setCoin] = useState('bitcoin');

  const coins = ['bitcoin', 'ethereum', 'binancecoin', 'solana'];

  // eslint-disable-next-line
  useEffect(() => {
    fetch(`${API}/indicators/${coin}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setData(data))
      .catch(() => {});
  }, [coin]);

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>► TECHNICAL INDICATORS</h3>
        <div style={styles.tabs}>
          {coins.map(c => (
            <button key={c} onClick={() => setCoin(c)} style={{
              ...styles.tab,
              color: coin === c ? '#60a5fa' : '#004422',
              borderColor: coin === c ? '#60a5fa' : '#004422',
            }}>
              {c === 'bitcoin' ? 'BTC' : c === 'ethereum' ? 'ETH' : c === 'binancecoin' ? 'BNB' : 'SOL'}
            </button>
          ))}
        </div>
      </div>

      {data && (
        <div style={styles.grid}>
          <div style={styles.indicator}>
            <span style={styles.label}>PRICE</span>
            <span style={styles.value}>₹{data.price_inr?.toLocaleString('en-IN')}</span>
          </div>
          <div style={styles.indicator}>
            <span style={styles.label}>MA7</span>
            <span style={styles.value}>₹{data.MA7?.toLocaleString('en-IN')}</span>
          </div>
          <div style={styles.indicator}>
            <span style={styles.label}>MA30</span>
            <span style={styles.value}>₹{data.MA30?.toLocaleString('en-IN')}</span>
          </div>
          <div style={styles.indicator}>
            <span style={styles.label}>RSI (14)</span>
            <span style={{
              ...styles.value,
              color: data.RSI > 70 ? '#ff4444' : data.RSI < 30 ? '#60a5fa' : '#F18F01'
            }}>
              {data.RSI} {data.RSI > 70 ? '⚠ OB' : data.RSI < 30 ? '🟢 OS' : '— N'}
            </span>
          </div>
          <div style={styles.indicator}>
            <span style={styles.label}>MACD</span>
            <span style={styles.value}>{data.MACD?.toFixed(2)}</span>
          </div>
          <div style={styles.indicator}>
            <span style={styles.label}>SIGNAL</span>
            <span style={styles.value}>{data.MACD_Signal?.toFixed(2)}</span>
          </div>
          <div style={styles.indicator}>
            <span style={styles.label}>BB UPPER</span>
            <span style={styles.value}>₹{data.BB_Upper?.toLocaleString('en-IN')}</span>
          </div>
          <div style={styles.indicator}>
            <span style={styles.label}>BB LOWER</span>
            <span style={styles.value}>₹{data.BB_Lower?.toLocaleString('en-IN')}</span>
          </div>
          <div style={{ ...styles.indicator, gridColumn: 'span 2' }}>
            <span style={styles.label}>OVERALL SIGNAL</span>
            <span style={{
              ...styles.value,
              fontSize: '16px',
              color: data.signal === 'BULLISH' ? '#60a5fa' : '#ff4444'
            }}>
              {data.signal === 'BULLISH' ? '▲ BULLISH' : '▼ BEARISH'}
            </span>
          </div>
        </div>
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
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
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '10px',
  },
  indicator: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    padding: '10px',
    background: 'rgba(0,255,136,0.03)',
    border: '1px solid rgba(30,58,110,0.5)',
    borderRadius: '2px',
  },
  label: {
    fontSize: '9px',
    color: '#334155',
    fontFamily: 'Courier New',
    letterSpacing: '1px',
  },
  value: {
    fontSize: '13px',
    color: '#60a5fa',
    fontFamily: 'Courier New',
    fontWeight: '600',
  },
};

export default IndicatorPanel;