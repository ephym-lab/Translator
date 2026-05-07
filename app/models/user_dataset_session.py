import uuid

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class UserDatasetSession(TimestampMixin, Base):
    """Tracks which dataset a user was assigned per language — prevents re-serving the same dataset."""

    __tablename__ = "user_dataset_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("unclean_datasets.id", ondelete="CASCADE"), nullable=False)
    language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        # A user cannot be assigned the same dataset for the same language twice.
        UniqueConstraint("user_id", "dataset_id", "language_id", name="uq_user_dataset_lang"),
    )

    # Relationships
    user = relationship("User")
    dataset = relationship("UncleanDataset")
    language = relationship("Language")
