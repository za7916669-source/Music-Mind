"""
Database connection setup.

Uses SQLite by default (zero-config, single file — perfect for local development).
To switch to PostgreSQL later (e.g. when you deploy), you only need to change
DATABASE_URL — nothing else in the codebase changes, since we access the DB
through SQLAlchemy's ORM rather than raw SQLite-specific code.

Example PostgreSQL URL (for later):
    postgresql://username:password@host:5432/similar_songs_db
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Configuration ---------------------------------------------------------
# Change this single line to switch databases later.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///similar_songs.db")

# SQLite needs this extra flag to allow use across threads (e.g. in a web API).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    """Yield a database session (use in a `with` block or FastAPI dependency later)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
