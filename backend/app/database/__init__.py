"""
Database package for QueryMind.

Exports the engine, session factory, get_db dependency, and ORM Base
so other modules can import from a single location.
"""

from app.database.connection import engine, get_db, SessionLocal
from app.database.models import Base

__all__ = ["engine", "get_db", "SessionLocal", "Base"]
