import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class RefreshToken(TimestampMixin, Base):
    """Stored refresh token for revocation support."""

    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(512), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
