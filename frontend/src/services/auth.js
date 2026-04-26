import api, { setAuthToken } from './api';

export const login = async (username, password) => {
  const resp = await api.post('/auth/login', { username, password });
  return resp.data;
};

export const completeLogin = (token, username, role) => {
  if (token) setAuthToken(token);
  if (username) localStorage.setItem('auth_username', username);
  if (role) localStorage.setItem('auth_role', role);
  window.dispatchEvent(new CustomEvent('authChanged', { detail: { username, role } }));
};

export const register = async (username, password, role, phone) => {
  const payload = { username, password, phone };
  if (role) payload.role = role;
  return api.post('/auth/register', payload);
};

export const logout = async () => {
  try {
    await api.post('/auth/logout');
  } catch (e) {
    // ignore errors
  }
  setAuthToken(null);
  localStorage.removeItem('auth_username');
  localStorage.removeItem('auth_role');
  window.dispatchEvent(new CustomEvent('authChanged', { detail: null }));
};

export const getAuth = () => {
  return {
    token: localStorage.getItem('auth_token'),
    username: localStorage.getItem('auth_username'),
    role: localStorage.getItem('auth_role'),
  };
};

const normalizePhoneNumber = (phoneNumber) => {
  const value = String(phoneNumber || '').trim();
  if (!value) {
    throw new Error('Phone number is required for OTP verification.');
  }
  if (!value.startsWith('+')) {
    throw new Error('Phone number must include the international prefix, e.g. +84123456789.');
  }
  return value;
};

export const sendOTP = (phoneNumber, recaptchaContainerId) => {
  // Dummy function - OTP disabled
  return Promise.resolve({ verificationId: 'dummy' });
};

export const verifyOTP = (confirmationResult, otpCode) => {
  // Dummy function - OTP disabled
  return Promise.resolve({ valid: true, error: null });
};

export default { login, register, logout, getAuth, completeLogin };
