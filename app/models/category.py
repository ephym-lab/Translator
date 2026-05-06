import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class Category(TimestampMixin, Base):
    """Dataset category (e.g. text, voice, sign_language)."""

    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
