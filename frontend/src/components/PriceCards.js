import React, { useState, useEffect } from 'react';

function PriceCards({ token, API }) {
  const [prices, setPrices] = useState([]);

  // eslint-disable-next-line
  useEffect(() => {
    fetch(`${API}/prices`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setPrices(data))
      .catch(() => {});
  }, []);

  return (
    <div style={styles.grid}>
      {prices.map((coin, i) => (
        <div key={i} style={styles.card}>
          <div style={styles.cardHeader}>
            <span style={styles.symbol}>{coin.symbol}</span>
            <span style={{
              ...styles.change,
              color: coin.price_change_pct_24h >= 0 ? '#60a5fa' : '#ff4444'
            }}>
              {coin.price_change_pct_24h >= 0 ? '▲' : '▼'} {Math.abs(coin.price_change_pct_24h).toFixed(2)}%
            </span>
          </div>
          <div style={styles.price}>₹{coin.price_inr.toLocaleString('en-IN')}</div>
          <div style={styles.cardFooter}>
            <span style={styles.label}>H: ₹{coin.high_24h?.toLocaleString('en-IN')}</span>
            <span style={styles.label}>L: ₹{coin.low_24h?.toLocaleString('en-IN')}</span>
          </div>
          <div style={styles.mcap}>
            MCap: ₹{(coin.market_cap_inr / 1e12).toFixed(2)}T
          </div>
        </div>
      ))}
    </div>
  );
}

const styles = {
  grid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' },
  card: { background: '#0d1b33', border: '1px solid #1e3a6e', borderRadius: '10px', padding: '16px' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' },
  symbol: { fontSize: '16px', fontWeight: '700', color: '#ffffff' },
  change: { fontSize: '12px', fontWeight: '600' },
  price: { fontSize: '18px', fontWeight: '700', color: '#60a5fa', marginBottom: '8px' },
  cardFooter: { display: 'flex', justifyContent: 'space-between', marginBottom: '4px' },
  label: { fontSize: '10px', color: '#64748b' },
  mcap: { fontSize: '10px', color: '#64748b', marginTop: '4px' },
};

export default PriceCards;