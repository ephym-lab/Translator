import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LanguageCreate(BaseModel):
    name: str
    code: str


class LanguageUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class LanguageResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    created_at: datetime

    model_config = {"from_attributes": True}
