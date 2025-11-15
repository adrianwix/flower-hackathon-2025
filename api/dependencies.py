"""
FastAPI dependencies for dependency injection.
"""

from typing import Generator
from sqlmodel import Session
from database import engine


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    Use this in FastAPI endpoints with Depends(get_session)
    """
    with Session(engine) as session:
        yield session
