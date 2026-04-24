import api, { setAuthToken } from './api';
import { initializeApp } from 'firebase/app';
import { getAuth as getFirebaseAuth, signInWithPhoneNumber, RecaptchaVerifier } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyAzbn-dR1HbBDkQpfykQh97JLJET5IQF8o",
  authDomain: "enterprise-portal-ac043.firebaseapp.com",
  projectId: "enterprise-portal-ac043",
  storageBucket: "enterprise-portal-ac043.appspot.com",
  messagingSenderId: "655304350864",
  appId: "1:655304350864:web:8766ba2f5586d264368c15",
  measurementId: "G-ETVMDTRE42",
};

const app = initializeApp(firebaseConfig);
const firebaseAuth = getFirebaseAuth(app);

const getRecaptchaVerifier = (containerId) => {
  if (typeof window === 'undefined') return null;
  if (!window.recaptchaVerifier) {
    window.recaptchaVerifier = new RecaptchaVerifier(containerId, {
      size: 'invisible',
      callback: (response) => {
        console.log('Recaptcha verified:', response);
      },
      'expired-callback': () => {
        if (window.recaptchaVerifier) {
          window.recaptchaVerifier.clear();
        }
      },
    }, firebaseAuth);
  }
  return window.recaptchaVerifier;
};

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
  const normalizedPhone = normalizePhoneNumber(phoneNumber);
  const recaptchaVerifier = getRecaptchaVerifier(recaptchaContainerId);
  if (!recaptchaVerifier) {
    throw new Error('Unable to initialize reCAPTCHA verification. Please refresh and try again.');
  }
  return signInWithPhoneNumber(firebaseAuth, normalizedPhone, recaptchaVerifier);
};

export const verifyOTP = (confirmationResult, otpCode) => {
  return confirmationResult.confirm(otpCode);
};

export default { login, register, logout, getAuth, completeLogin, sendOTP, verifyOTP };
