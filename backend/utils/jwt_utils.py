import os
import time
from datetime import datetime, timedelta
import jwt

JWT_SECRET = os.getenv("AUTH_JWT_SECRET", os.getenv("JWT_SECRET", "change-me-in-prod"))
JWT_ALGO = os.getenv("AUTH_JWT_ALGO", "HS256")
JWT_EXP_MINUTES = int(os.getenv("AUTH_JWT_EXP_MINUTES", "60"))


def create_access_token(subject: str, jti: str, minutes: int = None, extra: dict = None) -> str:
    exp_minutes = minutes or JWT_EXP_MINUTES
    now = datetime.utcnow()
    now_ts = int(time.time())
    payload = {
        "sub": subject,
        "jti": jti,
        "iat": now_ts,
        "exp": now_ts + int(exp_minutes * 60),
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except Exception:
        raise
