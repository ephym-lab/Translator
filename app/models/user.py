import uuid
import enum

from sqlalchemy import Column, String, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(TimestampMixin, Base):
    """Platform user — contributor, validator, or admin."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    avatar = Column(String(500), nullable=True)
    gender = Column(SAEnum(GenderEnum, name="gender_enum"), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SAEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.user, server_default="user")
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user_languages = relationship("UserLanguage", back_populates="user", cascade="all, delete-orphan")
    languages = relationship("Language", secondary="user_languages", viewonly=True)
    responses = relationship("Response", back_populates="user")
    votes = relationship("ResponseVote", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
