from fastapi.testclient import TestClient
import os
import pytest
from backend.main import app
from backend.database.auth_db import engine as auth_engine
from backend.models.base import Base
from backend.database.session import SessionAuth
from backend.utils.security import hash_password
from backend.models.auth_models import AuthUser

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_auth_db():
    # ensure AUTH_DB tables exist for tests
    Base.metadata.create_all(bind=auth_engine)
    # cleanup before/after
    yield
    Base.metadata.drop_all(bind=auth_engine)


def test_login_logout_refresh():
    # create test user
    s = SessionAuth()
    try:
        user = AuthUser(username="test.user@example.com", password_hash=hash_password("Secret1!"), role="Admin")
        s.add(user)
        s.commit()
        s.refresh(user)
        # login
        resp = client.post("/auth/login", json={"username": "test.user@example.com", "password": "Secret1!"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        token = data["access_token"]
        # refresh
        resp2 = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert "access_token" in data2
        new_token = data2["access_token"]
        # logout old token (first token still valid until revoked by refresh)
        resp3 = client.post("/auth/logout", headers={"Authorization": f"Bearer {new_token}"})
        assert resp3.status_code == 200
    finally:
        s.close()

*** End Patch