from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)


class Base(AsyncAttrs, DeclarativeBase):
    """Async-compatible declarative base for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """Adds created_at and updated_at columns to any model."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
