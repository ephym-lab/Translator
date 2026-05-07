import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.tribe import TribeResponse


class SubTribeCreate(BaseModel):
    name: str
    tribe_id: uuid.UUID


class SubTribeUpdate(BaseModel):
    name: Optional[str] = None
    tribe_id: Optional[uuid.UUID] = None

class SubTribeData(BaseModel):
    id: uuid.UUID
    name: str
    tribe_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}

class SubTribeResponse(BaseModel):
    message: str
    data: SubTribeData
    


class SubTribeNestedResponse(BaseModel):
    """SubTribe with its parent Tribe — used in nested language responses."""
    id: uuid.UUID
    name: str
    tribe: TribeResponse

    model_config = {"from_attributes": True}
