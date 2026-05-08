import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TribeCreate(BaseModel):
    name: str
    country: str
    country_code: str


class TribeUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None


class TribeData(BaseModel):
    id: uuid.UUID
    name: str
    country: str
    country_code: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TribeResponse(BaseModel):
    data:TribeData
