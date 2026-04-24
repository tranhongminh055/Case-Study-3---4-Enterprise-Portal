"""
OTP Token model for database
Stores OTP codes for verification
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum as SQLEnum
from datetime import datetime
import enum
from backend.models.base import Base


class OTPTokenStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"


class OTPToken(Base):
    """
    OTP Token model for temporary OTP storage
    """
    __tablename__ = "otp_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # OTP Code
    otp_code = Column(String(10), nullable=False)
    
    # Recipient info (email or phone)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Purpose: "login" or "register"
    purpose = Column(String(50), nullable=False)
    
    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Status
    verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    
    def is_expired(self) -> bool:
        """Check if OTP has expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if OTP is still valid (not expired, not verified)"""
        return not self.is_expired() and not self.verified
    
    def __repr__(self):
        return f"<OTPToken {self.email or self.phone} - {self.purpose}>"
