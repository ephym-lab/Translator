import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class OTP(TimestampMixin, Base):
    """Stores one-time password codes for email verification."""

    __tablename__ = "otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
