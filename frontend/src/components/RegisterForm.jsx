import { useState } from 'react';
import { register, login, completeLogin } from '../services/auth';

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

export default function RegisterForm({ onSuccess, onCancel }) {
  const [username, setUsername] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Employee');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await register(username, password, role, phone.trim());
      
      // Auto login after registration
      const authResponse = await login(username, password);
      completeLogin(authResponse.access_token, username, authResponse.role);
      
      if (onSuccess) onSuccess({ username });
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data || err.message || 'Register failed';
      setError(formatErrorMessage(errorDetail));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <h3>Create account</h3>
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
        Phone number
        <input
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="+84123456789"
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
      <label>
        Vai trò
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="Employee">Nhân viên</option>
          <option value="HR Manager">Nhân sự</option>
          <option value="Payroll Manager">Quản lý Lương</option>
          <option value="Admin">Quản trị viên</option>
        </select>
      </label>
      <div className="form-actions">
        <button type="submit" disabled={isLoading}>Register</button>
        <button type="button" onClick={onCancel}>Back to login</button>
      </div>
    </form>
  );
}
