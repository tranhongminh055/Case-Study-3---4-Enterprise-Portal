"""Initialize AUTH_DB and optionally create a bootstrap admin user.

Usage (from project root):
    python backend/scripts/init_auth_db.py

It reads BOOTSTRAP_ADMIN_USERNAME and BOOTSTRAP_ADMIN_PASSWORD from environment
or from backend/.env if present.
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from backend.database.auth_db import engine as auth_engine, ensure_auth_db_schema
from backend.models.base import Base
from backend.database.session import SessionAuth
from backend.utils.security import hash_password
from backend.models.auth_models import AuthUser


def ensure_tables():
    Base.metadata.create_all(bind=auth_engine)
    ensure_auth_db_schema()


def create_bootstrap_admin(username: str, password: str):
    s = SessionAuth()
    try:
        existing = s.query(AuthUser).filter(AuthUser.username == username).one_or_none()
        if existing:
            print(f"Admin user '{username}' already exists (id={existing.id})")
            return
        user = AuthUser(username=username, password_hash=hash_password(password), role="Admin")
        s.add(user)
        s.commit()
        s.refresh(user)
        print(f"Created admin user '{username}' (id={user.id})")
    finally:
        s.close()


if __name__ == "__main__":
    ensure_tables()
    user = os.getenv('BOOTSTRAP_ADMIN_USERNAME', 'admin@example.com')
    pwd = os.getenv('BOOTSTRAP_ADMIN_PASSWORD', 'Admin123!')
    create_bootstrap_admin(user, pwd)
