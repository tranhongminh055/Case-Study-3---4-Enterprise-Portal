import { useState } from 'react';
import { login, completeLogin, sendOTP, verifyOTP } from '../services/auth';
import OTPVerificationForm from './OTPVerificationForm';

export default function LoginForm({ onSuccess, onCancel }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState(null);
  const [isOTPStage, setIsOTPStage] = useState(false);
  const [confirmationResult, setConfirmationResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingToken, setPendingToken] = useState(null);
  const [pendingRole, setPendingRole] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setErrorMessage('');
    setIsLoading(true);
    try {
      const authResponse = await login(username, password);
      const phoneNumber = authResponse.phone || phone.trim();
      if (!phoneNumber) {
        throw new Error('Phone number required for OTP verification');
      }
      if (!phoneNumber.startsWith('+')) {
        throw new Error('Phone number must include the international prefix, e.g. +84123456789.');
      }
      const result = await sendOTP(phoneNumber, 'recaptcha-container');
      setConfirmationResult(result);
      setPendingToken(authResponse.access_token);
      setPendingRole(authResponse.role);
      setIsOTPStage(true);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (otpCode) => {
    try {
      setIsLoading(true);
      await verifyOTP(confirmationResult, otpCode);
      if (pendingToken) {
        completeLogin(pendingToken, username, pendingRole);
      }
      if (onSuccess) onSuccess({ username, role: pendingRole });
    } catch (error) {
      setErrorMessage('Invalid OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setErrorMessage('');
    try {
      const phoneNumber = phone.trim();
      const result = await sendOTP(phoneNumber, 'recaptcha-container');
      setConfirmationResult(result);
    } catch (error) {
      setErrorMessage('Unable to resend OTP. Please refresh and try again.');
    }
  };

  return (
    <div>
      {!isOTPStage ? (
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
            Phone number (required if not saved on account)
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+84123456789"
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
