import uuid

from sqlalchemy import Column, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


class Response(TimestampMixin, Base):
    """A contributor's response to an UncleanDataset entry in a specific language."""

    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    response_text = Column(Text, nullable=False)
    response_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)
    is_ai_generated = Column(Boolean, default=False, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("unclean_datasets.id"), nullable=False)
    language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    __table_args__ = (
        # A user can respond to the same dataset in multiple languages,
        # but NOT twice in the same language for the same dataset.
        UniqueConstraint("user_id", "dataset_id", "language_id", name="uq_user_dataset_language"),
        Index("uq_ai_response", "dataset_id", "language_id", "category_id", unique=True, postgresql_where=(is_ai_generated == True)),
    )

    # Relationships
    user = relationship("User", back_populates="responses")
    dataset = relationship("UncleanDataset", back_populates="responses")
    language = relationship("Language")
    category = relationship("Category")
    votes = relationship("ResponseVote", back_populates="response", cascade="all, delete-orphan")

    @property
    def acceptance_count(self) -> int:
        return sum(1 for v in self.votes if getattr(v.vote, 'value', v.vote) == "accept")

    @property
    def rejection_count(self) -> int:
        return sum(1 for v in self.votes if getattr(v.vote, 'value', v.vote) == "reject")
