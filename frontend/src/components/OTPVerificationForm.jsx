import React, { useState } from 'react';
import './OTPVerificationForm.css';

const OTPVerificationForm = ({ onSubmit, onResend, isLoading, errorMessage }) => {
  const [otp, setOtp] = useState('');

  const handleChange = (e) => {
    setOtp(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (otp.trim().length === 6) {
      onSubmit(otp);
    }
  };

  return (
    <div className="otp-verification-form">
      <h2>Verify OTP</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={otp}
          onChange={handleChange}
          maxLength={6}
          placeholder="Enter OTP"
          className={errorMessage ? 'input-error' : ''}
        />
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        <button type="submit" disabled={isLoading || otp.trim().length !== 6}>
          {isLoading ? 'Verifying...' : 'Verify OTP'}
        </button>
      </form>
      <button onClick={onResend} disabled={isLoading} className="resend-button">
        Resend OTP
      </button>
    </div>
  );
};

export default OTPVerificationForm;