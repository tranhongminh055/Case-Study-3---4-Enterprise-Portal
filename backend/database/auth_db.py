import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load backend .env before reading database settings.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# AUTH_DB connection - default to a local sqlite file for AUTH_DB if not provided
AUTH_DB_URL = os.getenv("AUTH_DB_URL")

if not AUTH_DB_URL:
    db_path = os.path.join(os.path.dirname(__file__), '..', 'auth_db.sqlite')
    AUTH_DB_URL = f"sqlite:///{db_path}"

engine = create_engine(AUTH_DB_URL, connect_args={"check_same_thread": False} if AUTH_DB_URL.startswith("sqlite") else {}, future=True)

from sqlalchemy import text

def ensure_auth_db_schema():
    if not AUTH_DB_URL.startswith("sqlite"):
        return

    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(auth_users)"))
        columns = [row[1] for row in result.fetchall()]
        if "phone" not in columns:
            conn.execute(text("ALTER TABLE auth_users ADD COLUMN phone VARCHAR(20)"))
            conn.commit()
