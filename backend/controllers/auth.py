from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4
from datetime import datetime

from backend.database.session import SessionAuth
from backend.models.auth_models import AuthUser, AuthToken, AuthLog
from backend.database.auth_db import engine as auth_engine, ensure_auth_db_schema
from backend.models.base import Base
from backend.utils.security import verify_password, hash_password
from backend.utils.jwt_utils import create_access_token, decode_token
from backend.utils.logger import logger
from backend.utils.validators import (
    validate_email, validate_password, validate_username, 
    validate_role, validate_login_input
)
from backend.services.otp_service import create_otp_token, verify_otp


Base.metadata.create_all(bind=auth_engine)
ensure_auth_db_schema()

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255, description="Email or username")
    password: str = Field(..., min_length=1, max_length=128, description="User password")

    @field_validator('username', 'password')
    def validate_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number for OTP")
    role: str = Field(default="Employee", description="User role")

    @field_validator('username')
    def validate_username_field(cls, v):
        is_valid, error = validate_username(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @field_validator('password')
    def validate_password_field(cls, v):
        is_valid, error = validate_password(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @field_validator('phone')
    def validate_phone_field(cls, v):
        phone = v.strip()
        if not phone.startswith('+'):
            raise ValueError('Phone number must include the international prefix, e.g. +84123456789')
        return phone

    @field_validator('role')
    def validate_role_field(cls, v):
        is_valid, error = validate_role(v)
        if not is_valid:
            raise ValueError(error)
        return v


class OTPVerificationRequest(BaseModel):
    otp_id: str = Field(..., description="OTP ID")
    otp_code: str = Field(..., description="OTP Code")


def log_event(db, user_id, username, action, endpoint, result, source_ip=None, details=None):
    entry = AuthLog(
        user_id=user_id,
        username=username,
        action=action,
        endpoint=endpoint,
        result=result,
        source_ip=source_ip,
        details=details,
    )
    db.add(entry)
    db.commit()


@router.post("/login")
def login(req: LoginRequest, request: Request):
    db = SessionAuth()
    try:
        user = db.query(AuthUser).filter(AuthUser.username == req.username).one_or_none()
        if not user:
            log_event(db, None, req.username, "login", "/login", "failure", request.client.host)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(req.password, user.password_hash):
            log_event(db, user.id, user.username, "login", "/login", "failure", request.client.host)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        jti = str(uuid4())
        token = create_access_token(subject=str(user.id), jti=jti, extra={"role": user.role, "username": user.username})

        # store token
        expires_at = datetime.utcnow()  # actual expiry embedded in token; rely on token exp
        token_rec = AuthToken(user_id=user.id, jti=jti, expires_at=expires_at, revoked=False)
        db.add(token_rec)
        db.commit()

        log_event(db, user.id, user.username, "login", "/login", "success", request.client.host)
        return {"access_token": token, "token_type": "bearer", "role": user.role, "phone": user.phone}
    finally:
        db.close()


@router.post("/logout")
def logout(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(None, 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    db = SessionAuth()
    try:
        t = db.query(AuthToken).filter(AuthToken.jti == jti).one_or_none()
        if t:
            t.revoked = True
            db.commit()
        log_event(db, user_id, payload.get("username"), "logout", "/logout", "success", request.client.host)
        return {"status": "ok"}
    finally:
        db.close()


@router.post("/refresh")
def refresh(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(None, 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    role = payload.get("role")
    username = payload.get("username")

    db = SessionAuth()
    try:
        t = db.query(AuthToken).filter(AuthToken.jti == jti).one_or_none()
        if not t or t.revoked:
            log_event(db, user_id, username, "refresh", "/refresh", "failure", request.client.host)
            raise HTTPException(status_code=401, detail="Token revoked")

        # revoke old
        t.revoked = True
        new_jti = str(uuid4())
        new_token = create_access_token(subject=str(user_id), jti=new_jti, extra={"role": role, "username": username})
        token_rec = AuthToken(user_id=user_id, jti=new_jti, expires_at=datetime.utcnow(), revoked=False)
        db.add(token_rec)
        db.commit()
        log_event(db, user_id, username, "refresh", "/refresh", "success", request.client.host)
        return {"access_token": new_token, "token_type": "bearer"}
    finally:
        db.close()


@router.post("/register", status_code=201)
def register(req: RegisterRequest, request: Request):
    """Create a new user in AUTH_DB. Default role is 'Employee'.
    Admins can create other roles by specifying `role`.
    Password is hashed with bcrypt; duplicates are rejected.
    """
    db = SessionAuth()
    try:
        # basic validation
        if not req.username or not req.password:
            log_event(db, None, req.username, "register", "/register", "failure", request.client.host)
            raise HTTPException(status_code=400, detail="username and password required")

        existing = db.query(AuthUser).filter(AuthUser.username == req.username).one_or_none()
        if existing:
            log_event(db, existing.id, req.username, "register", "/register", "failure", request.client.host)
            raise HTTPException(status_code=409, detail="username already exists")

        role = req.role or "Employee"
        # create user
        pw_hash = hash_password(req.password)
        user = AuthUser(username=req.username, password_hash=pw_hash, phone=req.phone, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        log_event(db, user.id, user.username, "register", "/register", "success", request.client.host)
        return {"id": user.id, "username": user.username, "role": user.role, "phone": user.phone}
    finally:
        db.close()


@router.post("/verify-otp")
def verify_otp_endpoint(req: OTPVerificationRequest):
    result = verify_otp(req.otp_id, req.otp_code)
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "OTP verified successfully", "details": result}


def get_current_user(request: Request, required_roles: list = None):
    """Validate bearer token, ensure not revoked, and optionally check roles.
    Returns dict payload on success or raises HTTPException.
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(None, 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    role = payload.get("role")

    db = SessionAuth()
    try:
        t = db.query(AuthToken).filter(AuthToken.jti == jti).one_or_none()
        if not t or t.revoked:
            raise HTTPException(status_code=401, detail="Token revoked or unknown")
    finally:
        db.close()

    if required_roles and role not in required_roles:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"user_id": user_id, "username": payload.get("username"), "role": role}
