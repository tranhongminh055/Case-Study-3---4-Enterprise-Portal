from fastapi import Request, HTTPException
from typing import Callable, List
from backend.database.session import SessionAuth
from backend.models.auth_models import AuthLog, AuthToken
from backend.utils.jwt_utils import decode_token
from backend.utils.logger import logger


def _write_log(user_id, username, action, endpoint, result, source_ip=None, details=None):
    try:
        db = SessionAuth()
        entry = AuthLog(user_id=user_id, username=username, action=action, endpoint=endpoint, result=result, source_ip=source_ip, details=details)
        db.add(entry)
        db.commit()
    except Exception:
        logger.exception("Failed to write RBAC audit log")
    finally:
        try:
            db.close()
        except Exception:
            pass


def require_auth(request: Request) -> dict:
    """Validate bearer token exists, not revoked. Return token payload.
    Raise HTTPException(401) if missing/invalid.
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        _write_log(None, None, request.method, request.url.path, "401", source_ip=(request.client.host if request.client else None))
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = auth.split(None, 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        _write_log(None, None, request.method, request.url.path, "401", source_ip=(request.client.host if request.client else None))
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # ensure token not revoked
    jti = payload.get("jti")
    user_id = payload.get("sub")
    username = payload.get("username")
    try:
        db = SessionAuth()
        t = db.query(AuthToken).filter(AuthToken.jti == jti).one_or_none()
        if not t or t.revoked:
            _write_log(user_id, username, request.method, request.url.path, "401", source_ip=(request.client.host if request.client else None))
            raise HTTPException(status_code=401, detail="Token revoked or unknown")
    finally:
        try:
            db.close()
        except Exception:
            pass

    return {"user_id": user_id, "username": username, "role": payload.get("role")}


def require_roles(allowed_roles: List[str]) -> Callable:
    def _dep(request: Request):
        payload = require_auth(request)
        role = payload.get("role")
        # Admin always allowed
        if role == "Admin":
            _write_log(payload.get("user_id"), payload.get("username"), request.method, request.url.path, "success", source_ip=(request.client.host if request.client else None))
            return payload
        if role not in allowed_roles:
            _write_log(payload.get("user_id"), payload.get("username"), request.method, request.url.path, "403", source_ip=(request.client.host if request.client else None))
            raise HTTPException(status_code=403, detail="Forbidden")
        _write_log(payload.get("user_id"), payload.get("username"), request.method, request.url.path, "success", source_ip=(request.client.host if request.client else None))
        return payload

    return _dep


def require_self_or_roles(id_param: str, allowed_roles: List[str]) -> Callable:
    """Dependency that allows access if user is Admin or in allowed_roles or the user is the same as id_param (Employee case).
    id_param is the name of the path parameter (e.g. 'employee_id').
    """
    def _dep(request: Request):
        payload = require_auth(request)
        role = payload.get("role")
        user_id = str(payload.get("user_id"))
        # Admin always allowed
        if role == "Admin":
            _write_log(payload.get("user_id"), payload.get("username"), request.method, request.url.path, "success", source_ip=(request.client.host if request.client else None))
            return payload

        # check role allowed
        if role in allowed_roles:
            _write_log(payload.get("user_id"), payload.get("username"), request.method, request.url.path, "success", source_ip=(request.client.host if request.client else None))
            return payload

        # otherwise, require the path param to equal the user id
        path_vals = request.path_params
        target_id = str(path_vals.get(id_param))
        if target_id and target_id == user_id:
            _write_log(payload.get("user_id"), payload.get("username"), request.method, request.url.path, "success", source_ip=(request.client.host if request.client else None))
            return payload

        _write_log(payload.get("user_id"), payload.get("username"), request.method, request.url.path, "403", source_ip=(request.client.host if request.client else None))
        raise HTTPException(status_code=403, detail="Forbidden")

    return _dep
