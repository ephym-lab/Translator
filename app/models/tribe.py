import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Tribe(TimestampMixin, Base):
    """Represents a major ethnic group (e.g. Kalenjin, Kikuyu)."""

    __tablename__ = "tribes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False,unique=True)
    country = Column(String(100), nullable=False)
    country_code = Column(String(5), nullable=False)

    # Relationships
    subtribes = relationship("SubTribe", back_populates="tribe")
