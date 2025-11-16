#!/usr/bin/env python3
"""
Database initialization script.
"""
from app.core.database import engine, Base
from app.core.config import settings

def init_database():
    """Create all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
