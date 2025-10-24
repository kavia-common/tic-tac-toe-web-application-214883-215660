import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# Read DB connection details from environment with sensible defaults pointing to the provided DB container
# PUBLIC_INTERFACE
def get_database_url() -> str:
    """Return the SQLAlchemy database URL from environment or a sensible default.

    Environment variables:
    - POSTGRES_URL: Full SQLAlchemy URL for Postgres. If present, used as-is.
    - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT: Used to compose the URL if POSTGRES_URL not set.
    - POSTGRES_HOST: Host for PostgreSQL (default 'tic_tac_toe_database' or 'localhost' in some environments).
    """
    env_url = os.getenv("POSTGRES_URL")
    if env_url:
        return env_url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "tic_tac_toe_database")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "postgres")

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


DATABASE_URL = get_database_url()


class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base."""
    pass


# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
