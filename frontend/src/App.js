import React, { useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

function App() {
  const [token, setToken] = useState(localStorage.getItem('cr_token') || '');

  const handleLogin = (newToken) => {
    localStorage.setItem('cr_token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('cr_token');
    setToken('');
  };

  return (
    <div>
      {token ? (
        <Dashboard token={token} onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;