import uuid
import enum

from sqlalchemy import Column, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class VoteEnum(str, enum.Enum):
    accept = "accept"
    reject = "reject"


class ResponseVote(TimestampMixin, Base):
    """A single vote cast by a user on a Response."""

    __tablename__ = "response_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    vote = Column(SAEnum(VoteEnum, name="vote_enum"), nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    response_id = Column(UUID(as_uuid=True), ForeignKey("responses.id"), nullable=False)

    # One vote per user per response
    __table_args__ = (
        UniqueConstraint("user_id", "response_id", name="uq_user_response_vote"),
    )

    # Relationships
    user = relationship("User", back_populates="votes")
    response = relationship("Response", back_populates="votes")
