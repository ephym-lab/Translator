import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SubTribeCreate(BaseModel):
    name: str
    tribe_id: uuid.UUID
    language_id: Optional[uuid.UUID] = None


class SubTribeUpdate(BaseModel):
    name: Optional[str] = None
    tribe_id: Optional[uuid.UUID] = None
    language_id: Optional[uuid.UUID] = None


class SubTribeResponse(BaseModel):
    id: uuid.UUID
    name: str
    tribe_id: uuid.UUID
    language_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}
