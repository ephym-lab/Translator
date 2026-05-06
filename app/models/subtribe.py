import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class SubTribe(TimestampMixin, Base):
    """A sub-group within a Tribe (e.g. Kipsigis within Kalenjin)."""

    __tablename__ = "subtribes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    tribe_id = Column(UUID(as_uuid=True), ForeignKey("tribes.id"), nullable=False)
    language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=True)

    # Relationships
    tribe = relationship("Tribe", back_populates="subtribes")
    language = relationship("Language", back_populates="subtribes")
