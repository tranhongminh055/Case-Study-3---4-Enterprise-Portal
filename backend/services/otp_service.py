"""
OTP Service using Firebase Authentication
Handles OTP generation, sending, and verification
"""

import os
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime, timedelta
import secrets
import string
from backend.database.session import SessionAuth
from backend.models.otp_token import OTPToken
from backend.utils.logger import logger


# Firebase initialization (use environment variable)
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS_JSON")
if FIREBASE_CREDENTIALS and not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.error(f"Firebase initialization failed: {str(e)}")


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP code
    
    Args:
        length: Length of OTP code (default 6 digits)
    
    Returns:
        Random OTP code as string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def send_otp_email(email: str, otp_code: str) -> bool:
    """
    Send OTP code via email using Firebase
    
    Args:
        email: Email address to send OTP to
        otp_code: The OTP code to send
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # This is a placeholder. In real implementation, use:
        # - SendGrid, AWS SES, or Firebase Cloud Functions
        # - For now, we'll log the OTP (NOT SECURE - for demo only)
        
        logger.info(f"OTP for {email}: {otp_code}")
        
        # In production, send real email:
        # import smtplib
        # from email.mime.text import MIMEText
        # ... send email code ...
        
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False


def send_otp_sms(phone: str, otp_code: str) -> bool:
    """
    Send OTP code via SMS
    
    Args:
        phone: Phone number to send OTP to
        otp_code: The OTP code to send
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use Twilio or Firebase Cloud Functions
        logger.info(f"OTP for {phone}: {otp_code}")
        
        # In production, use Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f"Your OTP is: {otp_code}",
        #     from_=twilio_number,
        #     to=phone
        # )
        
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP SMS to {phone}: {str(e)}")
        return False


def create_otp_token(
    email: str = None,
    phone: str = None,
    purpose: str = "login",
    expiry_minutes: int = 5
) -> dict:
    """
    Create and store OTP token in database
    
    Args:
        email: Email address (for email-based OTP)
        phone: Phone number (for SMS-based OTP)
        purpose: "login" or "register"
        expiry_minutes: OTP expiration time in minutes
    
    Returns:
        Dictionary with otp_id, otp_code, and expiry info
    """
    db = SessionAuth()
    try:
        otp_code = generate_otp(6)
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=expiry_minutes)
        
        # Create OTP token record
        otp_token = OTPToken(
            otp_code=otp_code,
            email=email,
            phone=phone,
            purpose=purpose,
            created_at=now,
            expires_at=expires_at,
            verified=False,
            attempts=0
        )
        
        db.add(otp_token)
        db.commit()
        db.refresh(otp_token)
        
        # Send OTP
        if email:
            send_otp_email(email, otp_code)
        elif phone:
            send_otp_sms(phone, otp_code)
        
        logger.info(f"OTP token created for {email or phone} (purpose: {purpose})")
        
        return {
            "otp_id": str(otp_token.id),
            "message": f"OTP sent to {email or phone}",
            "expires_at": expires_at.isoformat(),
            "expires_in_minutes": expiry_minutes
        }
    except Exception as e:
        logger.error(f"Failed to create OTP token: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_otp(otp_id: str, otp_code: str, max_attempts: int = 3) -> dict:
    """
    Verify OTP code
    
    Args:
        otp_id: ID of the OTP token
        otp_code: Code entered by user
        max_attempts: Maximum verification attempts allowed
    
    Returns:
        Dictionary with verification result
    """
    db = SessionAuth()
    try:
        otp_token = db.query(OTPToken).filter(OTPToken.id == otp_id).one_or_none()
        
        if not otp_token:
            logger.warning(f"OTP token not found: {otp_id}")
            return {"valid": False, "error": "OTP token not found"}
        
        # Check if expired
        if datetime.utcnow() > otp_token.expires_at:
            logger.warning(f"OTP token expired: {otp_id}")
            return {"valid": False, "error": "OTP has expired. Please request a new one."}
        
        # Check if already verified
        if otp_token.verified:
            logger.warning(f"OTP already verified: {otp_id}")
            return {"valid": False, "error": "OTP already used"}
        
        # Check max attempts
        if otp_token.attempts >= max_attempts:
            logger.warning(f"Max OTP attempts exceeded: {otp_id}")
            return {"valid": False, "error": "Too many attempts. Please request a new OTP."}
        
        # Verify code
        if otp_token.otp_code == otp_code:
            otp_token.verified = True
            otp_token.verified_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"OTP verified successfully: {otp_id}")
            return {
                "valid": True,
                "email": otp_token.email,
                "phone": otp_token.phone,
                "purpose": otp_token.purpose,
                "message": "OTP verified successfully"
            }
        else:
            # Increment attempts
            otp_token.attempts += 1
            db.commit()
            
            remaining = max_attempts - otp_token.attempts
            logger.warning(f"Invalid OTP attempt for {otp_id}. Remaining: {remaining}")
            
            return {
                "valid": False,
                "error": f"Invalid OTP. {remaining} attempts remaining.",
                "attempts_remaining": remaining
            }
    except Exception as e:
        logger.error(f"OTP verification failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def resend_otp(otp_id: str) -> dict:
    """
    Resend OTP code (invalidate old, create new)
    
    Args:
        otp_id: ID of the OTP token to resend
    
    Returns:
        Dictionary with new OTP info
    """
    db = SessionAuth()
    try:
        old_otp = db.query(OTPToken).filter(OTPToken.id == otp_id).one_or_none()
        
        if not old_otp:
            return {"valid": False, "error": "OTP token not found"}
        
        # Mark old OTP as expired
        old_otp.expires_at = datetime.utcnow()
        db.commit()
        
        # Create new OTP
        return create_otp_token(
            email=old_otp.email,
            phone=old_otp.phone,
            purpose=old_otp.purpose,
            expiry_minutes=5
        )
    except Exception as e:
        logger.error(f"Failed to resend OTP: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_expired_otps() -> int:
    """
    Delete expired OTP tokens (cleanup task)
    
    Returns:
        Number of deleted OTP tokens
    """
    db = SessionAuth()
    try:
        count = db.query(OTPToken).filter(
            OTPToken.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        
        logger.info(f"Cleaned up {count} expired OTP tokens")
        return count
    except Exception as e:
        logger.error(f"Failed to cleanup expired OTPs: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
