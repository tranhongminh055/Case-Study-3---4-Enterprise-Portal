import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load backend .env before reading database settings.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "payroll")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")

encoded_user = quote_plus(MYSQL_USER)
encoded_password = quote_plus(MYSQL_PASSWORD)

# ensure connection uses UTF-8 (utf8mb4) so accented characters are preserved
connection_url = (
    f"mysql+pymysql://{encoded_user}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    future=True,
    connect_args={"charset": "utf8mb4"},
)
