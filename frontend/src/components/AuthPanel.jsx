import { useEffect, useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import { getAuth, logout } from '../services/auth';

export default function AuthPanel() {
  const [auth, setAuth] = useState(getAuth());
  const [mode, setMode] = useState(null); // 'login'|'register'|null

  useEffect(() => {
    function onAuth(e) {
      setAuth(getAuth());
      setMode(null);
    }
    window.addEventListener('authChanged', onAuth);
    return () => window.removeEventListener('authChanged', onAuth);
  }, []);

  const handleLogout = async () => {
    await logout();
    setAuth(getAuth());
  };

  if (auth?.token) {
    return (
      <div className="auth-panel">
        <span className="auth-user">{auth.username || 'user'} ({auth.role || 'role'})</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    );
  }

  if (mode) {
    return (
      <div className="auth-modal-overlay" onClick={() => setMode(null)}>
        <div className="auth-modal-container" onClick={(e) => e.stopPropagation()}>
          <button className="auth-modal-close" onClick={() => setMode(null)}>✕</button>
          {mode === 'login' && <LoginForm onSuccess={() => setMode(null)} onCancel={() => setMode(null)} />}
          {mode === 'register' && <RegisterForm onSuccess={() => setMode('login')} onCancel={() => setMode(null)} />}
        </div>
      </div>
    );
  }

  return (
    <div className="auth-panel">
      <button onClick={() => setMode('login')}>Login</button>
      <button onClick={() => setMode('register')}>Register</button>
    </div>
  );
}
