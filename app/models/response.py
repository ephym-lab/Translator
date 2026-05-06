import uuid

from sqlalchemy import Column, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


class Response(TimestampMixin, Base):
    """A contributor's response to an UncleanDataset entry."""

    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    response_text = Column(Text, nullable=False)
    response_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("unclean_datasets.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="responses")
    dataset = relationship("UncleanDataset", back_populates="responses")
    votes = relationship("ResponseVote", back_populates="response", cascade="all, delete-orphan")
