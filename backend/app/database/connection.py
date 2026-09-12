"""
Database connection and session management for QueryMind.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables from backend/.env
load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://apple@localhost:5432/querymind",
)

engine = create_engine(
    DATABASE_URL,
    echo=False,          # Set True to log SQL for debugging
    pool_pre_ping=True,  # Verify connections before use
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Session:
    """
    FastAPI dependency that provides a database session.
    Ensures the session is closed after the request.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
