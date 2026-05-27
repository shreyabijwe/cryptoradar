import React, { useState, useEffect } from 'react';
import PriceCards from './PriceCards';
import PriceChart from './PriceChart';
import SentimentChart from './SentimentChart';
import IndicatorPanel from './IndicatorPanel';
import ForecastChart from './ForecastChart';
import NewsFeed from './NewsFeed';

const API = 'https://cryptoradar-api.onrender.com';

function Dashboard({ token, onLogout }) {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activePage, setActivePage] = useState('Dashboard');
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  const headers = { 'Authorization': `Bearer ${token}` };

  // eslint-disable-next-line
  useEffect(() => {
    fetch(`${API}/kpis`, { headers })
      .then(res => res.json())
      .then(data => { setKpis(data); setLoading(false); })
      .catch(() => setLoading(false));

    const timer = setInterval(() => setCurrentTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = ['Dashboard', 'Prices', 'Indicators', 'Sentiment', 'Forecast', 'News'];

  const renderPage = () => {
    switch (activePage) {
      case 'Prices':     return <div style={styles.page}><h2 style={styles.pageTitle}>Live Prices</h2><PriceCards token={token} API={API} /></div>;
      case 'Indicators': return <div style={styles.page}><h2 style={styles.pageTitle}>Technical Indicators</h2><IndicatorPanel token={token} API={API} /></div>;
      case 'Sentiment':  return <div style={styles.page}><h2 style={styles.pageTitle}>Market Sentiment</h2><SentimentChart token={token} API={API} /></div>;
      case 'Forecast':   return <div style={styles.page}><h2 style={styles.pageTitle}>Price Forecast</h2><ForecastChart token={token} API={API} /></div>;
      case 'News':       return <div style={styles.page}><h2 style={styles.pageTitle}>News Feed</h2><NewsFeed token={token} API={API} /></div>;
      default: return (
        <>
          <PriceCards token={token} API={API} />
          <div style={styles.row}>
            <PriceChart token={token} API={API} />
            <SentimentChart token={token} API={API} />
          </div>
          <div style={styles.row}>
            <IndicatorPanel token={token} API={API} />
            <ForecastChart token={token} API={API} />
          </div>
        </>
      );
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.topbar}>
        <div style={styles.topLeft}>
          <span style={styles.logo}>₿ CryptoRadar</span>
          <span style={styles.live}>● LIVE</span>
        </div>
        <div style={styles.topNav}>
          {navItems.map(item => (
            <div key={item} onClick={() => setActivePage(item)} style={{
              ...styles.navItem,
              color: activePage === item ? '#60a5fa' : '#64748b',
              borderBottom: activePage === item ? '2px solid #2563eb' : '2px solid transparent',
            }}>
              {item}
            </div>
          ))}
        </div>
        <div style={styles.topRight}>
          <span style={styles.time}>{currentTime}</span>
          <button onClick={onLogout} style={styles.logoutBtn}>Logout</button>
        </div>
      </div>

      {kpis && (
        <div style={styles.kpiBar}>
          <span style={styles.kpiItem}>Market Cap: ₹{(kpis.total_market_cap_inr / 1e12).toFixed(2)}T</span>
          <span style={styles.kpiDivider}>|</span>
          <span style={styles.kpiItem}>Best 24H: {kpis.best_performer_24h} ▲</span>
          <span style={styles.kpiDivider}>|</span>
          <span style={styles.kpiItem}>Worst 24H: {kpis.worst_performer_24h} ▼</span>
          <span style={styles.kpiDivider}>|</span>
          <span style={styles.kpiItem}>Sentiment: {kpis.avg_market_sentiment > 0 ? '▲ Bullish' : '▼ Bearish'}</span>
          <span style={styles.kpiDivider}>|</span>
          <span style={styles.kpiItem}>Coins: {kpis.coins_tracked}</span>
        </div>
      )}

      <div style={styles.main}>
        {loading ? <p style={{ color: '#60a5fa', padding: '40px' }}>Loading market data...</p> : renderPage()}
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#070b14' },
  topbar: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', height: '56px', background: '#0d1b33', borderBottom: '1px solid #1e3a6e' },
  topLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  logo: { fontSize: '16px', fontWeight: '700', color: '#ffffff' },
  live: { fontSize: '10px', color: '#34d399', letterSpacing: '1px' },
  topNav: { display: 'flex', gap: '4px' },
  navItem: { padding: '18px 14px', cursor: 'pointer', fontSize: '13px', fontWeight: '500', transition: 'color 0.2s' },
  topRight: { display: 'flex', alignItems: 'center', gap: '16px' },
  time: { fontSize: '12px', color: '#64748b' },
  logoutBtn: { padding: '6px 14px', background: 'transparent', color: '#f87171', border: '1px solid #f87171', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' },
  kpiBar: { display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 24px', background: '#0a0f1e', borderBottom: '1px solid #1e3a6e', fontSize: '12px', overflowX: 'auto' },
  kpiItem: { color: '#94a3b8', whiteSpace: 'nowrap' },
  kpiDivider: { color: '#1e3a6e' },
  main: { padding: '20px 24px' },
  row: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' },
  page: { padding: '8px 0' },
  pageTitle: { fontSize: '18px', fontWeight: '600', color: '#ffffff', marginBottom: '16px' },
};

export default Dashboard;