import os
from dotenv import load_dotenv

# Load .env from the backend folder to ensure DB env vars are available
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.controllers.employees import router as employee_router
from backend.controllers.auth import router as auth_router
from backend.controllers.departments import router as department_router
from backend.controllers.positions import router as position_router
from backend.controllers.payroll import router as payroll_router
from backend.controllers.reports import router as reports_router
from backend.controllers.alerts import router as alerts_router
from backend.utils.logger import logger
from backend.utils.errors import AppError, InternalError
from backend.database.session import SessionAuth
from backend.models.auth_models import AuthLog
from backend.utils.jwt_utils import decode_token

app = FastAPI(title="Enterprise Integration API")

frontend_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:5174,http://localhost:5175")
allow_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router)
app.include_router(auth_router)
app.include_router(department_router)
app.include_router(position_router)
app.include_router(payroll_router)
app.include_router(reports_router)
app.include_router(alerts_router)

if os.getenv("ENABLE_TEST_FAILURE_HOOKS", "false").lower() == "true":
    from backend.controllers.test_hooks import router as test_router
    app.include_router(test_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("API call %s %s", request.method, request.url.path)
    # attempt to write audit log to AUTH_DB when possible
    auth_header = request.headers.get("Authorization")
    user_id = None
    username = None
    try:
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(None, 1)[1]
            try:
                payload = decode_token(token)
                user_id = payload.get("sub")
                username = payload.get("username")
            except Exception:
                # invalid/expired token - still proceed to logging as unauthenticated
                pass

        response = await call_next(request)
        # write auth log (best-effort)
        try:
            db = SessionAuth()
            entry = AuthLog(user_id=user_id, username=username, action=request.method, endpoint=request.url.path, result=str(response.status_code), source_ip=request.client.host if request.client else None)
            db.add(entry)
            db.commit()
        except Exception:
            logger.exception("Failed to write audit log to AUTH_DB")
        finally:
            try:
                db.close()
            except Exception:
                pass

        logger.info("API response %s %s %s", request.method, request.url.path, response.status_code)
        return response
    except Exception as exc:
        logger.exception("Unhandled API exception %s %s", request.method, request.url.path)
        raise exc


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "message": exc.detail.get("message", str(exc.detail))},
    )


@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.exception("Server error: %s", exc)
    error = InternalError("An unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content={"status": 500, "message": str(error.detail.get("message", "Internal server error"))},
    )


@app.get("/health", response_model=dict)
def health_check():
    return {"status": "ok", "service": "enterprise_integration"}
