"""SQLAlchemy PostgreSQL engine, session factory, and FastAPI dependency."""

from collections.abc import Generator
import socket
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL, DB_HOSTADDR

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. Ensure backend/.env contains a valid PostgreSQL URI."
    )

_connect_args: dict[str, str] = {}
_parsed_url = make_url(DATABASE_URL)
if _parsed_url.host and DB_HOSTADDR:
    try:
        socket.getaddrinfo(_parsed_url.host, _parsed_url.port or 5432)
    except socket.gaierror:
        # Preserve TLS/SNI against the real hostname while routing TCP when local DNS lags
        _connect_args["hostaddr"] = DB_HOSTADDR

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


def get_db() -> Generator[Session, None, None]:
    """Yield a scoped SQLAlchemy database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
