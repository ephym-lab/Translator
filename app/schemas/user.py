import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import GenderEnum


class UserCreate(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    gender: GenderEnum
    phone: Optional[str] = None
    avatar: Optional[str] = None
    language_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    language_id: Optional[uuid.UUID] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    name: str
    email: EmailStr
    gender: GenderEnum
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_verified: bool
    is_active: bool
    language_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class OTPVerify(BaseModel):
    email: EmailStr
    code: str
