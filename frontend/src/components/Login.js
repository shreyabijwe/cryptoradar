import React, { useState } from 'react';

const API = 'https://cryptoradar-api.onrender.com';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (res.ok) {
        onLogin(data.access_token);
      } else {
        setError('Invalid username or password');
      }
    } catch (err) {
      setError('Cannot connect to server. Make sure the API is running.');
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <span style={styles.logoIcon}>₿</span>
          <h1 style={styles.title}>CryptoRadar</h1>
          <p style={styles.subtitle}>Real-Time Crypto Analytics</p>
          <div style={styles.ticker}>
            <span style={styles.tickerItem}>BTC ▲</span>
            <span style={styles.tickerItem}>ETH ▼</span>
            <span style={styles.tickerItem}>SOL ▲</span>
            <span style={styles.tickerItem}>BNB ▲</span>
          </div>
        </div>
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Username</label>
            <input style={styles.input} type="text" value={username}
              onChange={(e) => setUsername(e.target.value)} placeholder="Enter username" required />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input style={styles.input} type="password" value={password}
              onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" required />
          </div>
          {error && <p style={styles.error}>{error}</p>}
          <button style={styles.button} type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
          <p style={styles.hint}>Use: admin / crypto2024</p>
        </form>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #070b14 0%, #0d1b33 100%)' },
  card: { background: '#0d1b33', borderRadius: '16px', padding: '48px 40px', width: '400px', border: '1px solid #1e3a6e' },
  header: { textAlign: 'center', marginBottom: '32px' },
  logoIcon: { fontSize: '32px' },
  title: { fontSize: '26px', fontWeight: '700', color: '#ffffff', marginTop: '8px' },
  subtitle: { fontSize: '13px', color: '#64748b', marginTop: '4px' },
  ticker: { display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '12px', padding: '8px', background: '#070b14', borderRadius: '6px' },
  tickerItem: { fontSize: '12px', color: '#60a5fa' },
  form: { display: 'flex', flexDirection: 'column', gap: '16px' },
  field: { display: 'flex', flexDirection: 'column', gap: '6px' },
  label: { fontSize: '13px', fontWeight: '500', color: '#94a3b8' },
  input: { padding: '11px 14px', borderRadius: '8px', border: '1px solid #1e3a6e', fontSize: '14px', outline: 'none', background: '#070b14', color: '#ffffff' },
  button: { padding: '12px', background: '#2563eb', color: '#ffffff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: 'pointer', marginTop: '8px' },
  error: { color: '#f87171', fontSize: '13px', textAlign: 'center' },
  hint: { textAlign: 'center', fontSize: '12px', color: '#334155' },
};

export default Login;