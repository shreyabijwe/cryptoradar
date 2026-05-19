import React, { useState, useEffect } from 'react';

function NewsFeed({ token, API }) {
  const [news, setNews] = useState([]);
  const [coin, setCoin] = useState('bitcoin');

  const coins = ['bitcoin', 'ethereum', 'binancecoin', 'solana'];

  // eslint-disable-next-line
  useEffect(() => {
    fetch(`${API}/news/${coin}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setNews(data))
      .catch(() => {});
  }, [coin]);

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>► NEWS FEED</h3>
        <div style={styles.tabs}>
          {coins.map(c => (
            <button key={c} onClick={() => setCoin(c)} style={{
              ...styles.tab,
              color: coin === c ? '#60a5fa' : '#334155',
              borderColor: coin === c ? '#60a5fa' : '#334155',
            }}>
              {c === 'bitcoin' ? 'BTC' : c === 'ethereum' ? 'ETH' : c === 'binancecoin' ? 'BNB' : 'SOL'}
            </button>
          ))}
        </div>
      </div>
      <div style={styles.newsList}>
        {news.map((item, i) => (
          <div key={i} style={styles.newsItem}>
            <div style={styles.newsHeader}>
              <span style={{
                ...styles.sentiment,
                color: item.sentiment_label === 'Positive' ? '#60a5fa' :
                       item.sentiment_label === 'Negative' ? '#ff4444' : '#004422'
              }}>
                {item.sentiment_label === 'Positive' ? '▲' :
                 item.sentiment_label === 'Negative' ? '▼' : '—'}
              </span>
              <span style={styles.source}>{item.source}</span>
              <span style={styles.polarity}>
                {item.polarity > 0 ? '+' : ''}{item.polarity?.toFixed(3)}
              </span>
            </div>
            <p style={styles.headline}>{item.headline}</p>
            <p style={styles.date}>{item.published_at?.slice(0, 10)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: '',
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
  newsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    maxHeight: '400px',
    overflowY: 'auto',
  },
  newsItem: {
    padding: '12px',
    background: 'rgba(0,255,136,0.02)',
    border: '1px solid rgba(30,58,110,0.5)',
    borderRadius: '2px',
  },
  newsHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '6px',
  },
  sentiment: {
    fontSize: '14px',
    fontWeight: '700',
  },
  source: {
    fontSize: '10px',
    color: '#334155',
    fontFamily: 'Courier New',
    flex: 1,
  },
  polarity: {
    fontSize: '10px',
    color: '#334155',
    fontFamily: 'Courier New',
  },
  headline: {
    fontSize: '12px',
    color: '#93c5fd',
    fontFamily: 'Courier New',
    lineHeight: '1.5',
    marginBottom: '4px',
  },
  date: {
    fontSize: '10px',
    color: '#003311',
    fontFamily: 'Courier New',
  },
};

export default NewsFeed;