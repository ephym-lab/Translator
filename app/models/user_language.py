import uuid

from sqlalchemy import Column, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class UserLanguage(TimestampMixin, Base):
    """Junction table: a user can speak/select multiple languages."""

    __tablename__ = "user_languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "language_id", name="uq_user_language"),
    )

    # Relationships
    user = relationship("User", back_populates="user_languages")
    language = relationship("Language", back_populates="user_languages")
