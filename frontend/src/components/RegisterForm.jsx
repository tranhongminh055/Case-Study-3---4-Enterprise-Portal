import { useState } from 'react';
import { register, login, completeLogin, sendOTP, verifyOTP } from '../services/auth';
import OTPVerificationForm from './OTPVerificationForm';

export default function RegisterForm({ onSuccess, onCancel }) {
  const [username, setUsername] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Employee');
  const [error, setError] = useState(null);
  const [isOTPStage, setIsOTPStage] = useState(false);
  const [confirmationResult, setConfirmationResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingCredentials, setPendingCredentials] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setErrorMessage('');
    if (!phone.trim()) {
      setError('Phone number is required for OTP verification');
      return;
    }
    setIsLoading(true);
    try {
      await register(username, password, role, phone.trim());
      const result = await sendOTP(phone.trim(), 'recaptcha-container');
      setConfirmationResult(result);
      setPendingCredentials({ username, password });
      setIsOTPStage(true);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Register failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (otpCode) => {
    try {
      setIsLoading(true);
      await verifyOTP(confirmationResult, otpCode);
      if (pendingCredentials) {
        const authResponse = await login(pendingCredentials.username, pendingCredentials.password);
        completeLogin(authResponse.access_token, pendingCredentials.username, authResponse.role);
      }
      if (onSuccess) onSuccess({ username });
    } catch (error) {
      setErrorMessage('Invalid OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setErrorMessage('');
    try {
      const result = await sendOTP(phone.trim(), 'recaptcha-container');
      setConfirmationResult(result);
    } catch (error) {
      setErrorMessage('Unable to resend OTP. Please refresh and try again.');
    }
  };

  return (
    <div>
      {!isOTPStage ? (
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
            Role
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option>Employee</option>
              <option>HR Manager</option>
              <option>Payroll Manager</option>
              <option>Admin</option>
            </select>
          </label>
          <div className="form-actions">
            <button type="submit" disabled={isLoading}>Register</button>
            <button type="button" onClick={onCancel}>Back to login</button>
          </div>
        </form>
      ) : (
        <OTPVerificationForm
          onSubmit={handleVerifyOTP}
          onResend={handleResend}
          isLoading={isLoading}
          errorMessage={errorMessage}
        />
      )}
      <div id="recaptcha-container"></div>
    </div>
  );
}
