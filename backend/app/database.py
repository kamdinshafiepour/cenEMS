"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine (the connection to PostgreSQL)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,      # Test connections before using
    pool_size=5,             # Keep 5 connections ready
    max_overflow=10          # Allow up to 10 extra connections if needed
)

# Create session factory (sessions handle transactions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models (our tables will inherit from this)
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes.
    Creates a database session, yields it, then closes it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
