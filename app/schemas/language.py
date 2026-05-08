import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.subtribe import SubTribeNestedResponse


class LanguageCreate(BaseModel):
    name: str
    code: str
    subtribe_id: Optional[uuid.UUID] = None


class LanguageUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    subtribe_id: Optional[uuid.UUID] = None


class LanguageData(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    subtribe_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class LanguageResponse(BaseModel):
    data: LanguageData


class LanguageNestedResponse(BaseModel):
    """Language with full nested subtribe → tribe — used in user profile responses."""
    id: uuid.UUID
    name: str
    code: str
    subtribe: Optional[SubTribeNestedResponse] = None

    model_config = {"from_attributes": True}
