from sqlalchemy.orm import sessionmaker
from .sqlserver import engine as sqlserver_engine
from .mysql import engine as mysql_engine
from .auth_db import engine as auth_engine

SessionSqlServer = sessionmaker(
    bind=sqlserver_engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

SessionMysql = sessionmaker(
    bind=mysql_engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

SessionAuth = sessionmaker(
    bind=auth_engine,
    autocommit=False,
    autoflush=False,
    future=True,
)
