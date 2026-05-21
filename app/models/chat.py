import uuid
import enum

from sqlalchemy import Column, String, Text, Boolean, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class SessionStatusEnum(str, enum.Enum):
    active = "active"
    closed = "closed"


class ChatSession(TimestampMixin, Base):
    """
    A bilateral chat session between two users.
    Each participant records their preferred language for this session —
    incoming messages to them will be translated into that language.
    """

    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # The two participants
    initiator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Each user's preferred language for this session (human-readable name, e.g. "english")
    initiator_language = Column(String(100), nullable=False, default="english")
    recipient_language = Column(String(100), nullable=False, default="english")

    status = Column(
        SAEnum(SessionStatusEnum, name="session_status_enum"),
        nullable=False,
        default=SessionStatusEnum.active,
        server_default="active",
    )

    # Only one session per pair (order-independent enforced at service level)
    __table_args__ = (
        UniqueConstraint("initiator_id", "recipient_id", name="uq_chat_session_pair"),
    )

    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(TimestampMixin, Base):
    """
    A single message within a ChatSession.
    Stores both the original text (in the sender's language) and the
    translated text (in the recipient's preferred language).
    """

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # The original message text as typed by the sender
    original_text = Column(Text, nullable=False)

    # The source language of the original_text (e.g. "swahili")
    source_language = Column(String(100), nullable=False)

    # The target language the message was translated into (e.g. "english")
    target_language = Column(String(100), nullable=False)

    # The translated version of original_text
    translated_text = Column(Text, nullable=True)

    # True when the translation succeeded; False if it fell back to original
    is_translated = Column(Boolean, default=False, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
