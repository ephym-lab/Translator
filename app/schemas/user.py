import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.models.user import GenderEnum, RoleEnum
from app.schemas.language import LanguageNestedResponse


class UserCreate(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    gender: GenderEnum
    phone: Optional[str] = None
    avatar: Optional[str] = None
    languages: List[uuid.UUID]  # at least one language required


class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    name: str
    email: EmailStr
    gender: GenderEnum
    role: RoleEnum
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_verified: bool
    is_active: bool
    languages: List[LanguageNestedResponse] = []
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


class AddLanguageRequest(BaseModel):
    language_id: uuid.UUID
