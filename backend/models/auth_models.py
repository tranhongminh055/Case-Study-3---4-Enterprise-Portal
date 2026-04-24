from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.models.base import Base


class AuthUser(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(512), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tokens = relationship("AuthToken", back_populates="user")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("auth_users.id"), nullable=False)
    jti = Column(String(256), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("AuthUser", back_populates="tokens")


class AuthLog(Base):
    __tablename__ = "auth_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, nullable=True)
    username = Column(String(150), nullable=True)
    action = Column(String(100), nullable=False)
    endpoint = Column(String(300), nullable=True)
    result = Column(String(50), nullable=False)
    source_ip = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
