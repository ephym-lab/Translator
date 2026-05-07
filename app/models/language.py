import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Language(TimestampMixin, Base):
    """Represents a spoken/written language in the platform (e.g. Kikuyu, Kiswahili)."""

    __tablename__ = "languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False, index=True)
    subtribe_id = Column(UUID(as_uuid=True), ForeignKey("subtribes.id"), nullable=True)

    # Relationships
    subtribe = relationship("SubTribe", back_populates="languages")
    user_languages = relationship("UserLanguage", back_populates="language", cascade="all, delete-orphan")
    users = relationship("User", secondary="user_languages", viewonly=True)
    unclean_datasets = relationship("UncleanDataset", back_populates="language")
