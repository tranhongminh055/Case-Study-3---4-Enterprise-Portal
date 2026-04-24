import bcrypt
from datetime import datetime
from backend.utils.jwt_utils import decode_token


def hash_password(password: str) -> str:
    pw = password.encode('utf-8')
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def token_payload(token: str) -> dict:
    return decode_token(token)
