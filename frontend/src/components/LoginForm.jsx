import { useState } from 'react';
import { login, completeLogin } from '../services/auth';

// Format error from backend (handles objects, arrays, strings)
const formatErrorMessage = (error) => {
  if (typeof error === 'string') return error;
  if (Array.isArray(error)) {
    return error.map(e => typeof e === 'object' ? (e.msg || JSON.stringify(e)) : e).join(', ');
  }
  if (error && typeof error === 'object') {
    if (error.msg) return error.msg;
    if (error.detail) return typeof error.detail === 'string' ? error.detail : formatErrorMessage(error.detail);
    return JSON.stringify(error);
  }
  return String(error);
};

export default function LoginForm({ onSuccess, onCancel }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const authResponse = await login(username, password);
      completeLogin(authResponse.access_token, username, authResponse.role);
      if (onSuccess) onSuccess({ username, role: authResponse.role });
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data || err.message || 'Login failed';
      setError(formatErrorMessage(errorDetail));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="auth-form">
      <h3>Sign in</h3>
      {error && <div className="alert error">{error}</div>}
      <label>
        Email
        <input
          type="email"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="you@example.com"
          required
        />
      </label>
      <label>
        Password
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </label>
      <div className="form-actions">
        <button type="submit" disabled={isLoading}>Login</button>
        <button type="button" onClick={onCancel}>Đăng ký</button>
      </div>
    </form>
  );
}
