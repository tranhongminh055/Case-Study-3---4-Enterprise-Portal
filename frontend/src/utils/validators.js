/**
 * Frontend validation utilities for user authentication
 */

export const validateEmail = (email) => {
  if (!email) return { valid: false, error: 'Email is required' };
  
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!pattern.test(email)) {
    return { valid: false, error: 'Invalid email format' };
  }
  
  if (email.length > 255) {
    return { valid: false, error: 'Email is too long (max 255 characters)' };
  }
  
  return { valid: true, error: '' };
};

export const validatePassword = (password) => {
  if (!password) return { valid: false, error: 'Password is required' };
  
  const errors = [];
  
  if (password.length < 8) {
    errors.push('at least 8 characters');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('at least one uppercase letter');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('at least one lowercase letter');
  }
  
  if (!/\d/.test(password)) {
    errors.push('at least one digit');
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{};:'"",.<>?/\\|`~]/.test(password)) {
    errors.push('at least one special character');
  }
  
  if (errors.length > 0) {
    return { valid: false, error: 'Password must contain: ' + errors.join(', ') };
  }
  
  if (password.length > 128) {
    return { valid: false, error: 'Password is too long (max 128 characters)' };
  }
  
  return { valid: true, error: '' };
};

export const validateUsername = (username) => {
  if (!username) return { valid: false, error: 'Username is required' };
  
  username = username.trim();
  
  if (username.length < 3) {
    return { valid: false, error: 'Username must be at least 3 characters' };
  }
  
  if (username.length > 50) {
    return { valid: false, error: 'Username must not exceed 50 characters' };
  }
  
  const pattern = /^[a-zA-Z0-9._-]+$/;
  if (!pattern.test(username)) {
    return { valid: false, error: 'Username can only contain letters, numbers, dots, hyphens, and underscores' };
  }
  
  return { valid: true, error: '' };
};

export const validateLoginForm = (username, password) => {
  if (!username) return { valid: false, error: 'Email/Username is required' };
  if (!password) return { valid: false, error: 'Password is required' };
  
  if (username.length > 255) {
    return { valid: false, error: 'Email/Username is too long' };
  }
  
  if (password.length > 128) {
    return { valid: false, error: 'Password is too long' };
  }
  
  return { valid: true, error: '' };
};

/**
 * Get password strength score (0-4)
 * Used for visual feedback
 */
export const getPasswordStrength = (password) => {
  if (!password) return 0;
  
  let strength = 0;
  
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/\d/.test(password)) strength++;
  
  return strength;
};

export const getPasswordStrengthLabel = (strength) => {
  switch (strength) {
    case 0:
    case 1:
      return 'Weak';
    case 2:
      return 'Fair';
    case 3:
      return 'Good';
    case 4:
      return 'Strong';
    default:
      return '';
  }
};
