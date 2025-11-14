#!/usr/bin/env python3
"""
Database initialization script.

This script creates all database tables and seeds initial data.
"""

from database import create_db_and_tables, get_session, init_pathologies


def main():
    """Initialize the database"""
    print("Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created successfully")

    print("\nInitializing pathologies...")
    session = next(get_session())
    init_pathologies(session)
    print("✓ Pathologies initialized")

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    main()
