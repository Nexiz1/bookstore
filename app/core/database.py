"""Database configuration module.

This module provides SQLAlchemy 2.0 style database setup with proper
transaction management using the Unit of Work pattern.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 style declarative base class.

    All models should inherit from this class.
    """

    pass


# SQLite용 connect_args 설정
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session.

    Yields:
        Session: SQLAlchemy database session.

    Note:
        The session is automatically closed after the request.
        Commit should be called explicitly by the service layer.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session (for non-FastAPI use).

    Yields:
        Session: SQLAlchemy database session.

    Example:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UnitOfWork:
    """Unit of Work pattern implementation for transaction management.

    This class ensures that all database operations within a business
    transaction are committed together or rolled back together.

    Usage:
        def create_order(self, user_id: int, order_data: OrderCreate):
            with UnitOfWork(self.db) as uow:
                order = self.order_repo.create(order_data, commit=False)
                for item in items:
                    self.order_repo.add_item(item, commit=False)
                uow.commit()  # All operations committed together
    """

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        """Commit all pending changes."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback all pending changes."""
        self.session.rollback()

    def flush(self) -> None:
        """Flush pending changes to get generated IDs without committing."""
        self.session.flush()
