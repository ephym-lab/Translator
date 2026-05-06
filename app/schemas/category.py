import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
