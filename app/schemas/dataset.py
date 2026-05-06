import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.unclean_dataset import DatasetLevelEnum


class DatasetCreate(BaseModel):
    original_text: str
    level: DatasetLevelEnum
    category_id: uuid.UUID
    language_id: uuid.UUID


class DatasetUpdate(BaseModel):
    original_text: Optional[str] = None
    level: Optional[DatasetLevelEnum] = None
    category_id: Optional[uuid.UUID] = None
    language_id: Optional[uuid.UUID] = None


class DatasetResponse(BaseModel):
    id: uuid.UUID
    original_text: str
    level: DatasetLevelEnum
    response_percentage: float
    is_clean: bool
    category_id: uuid.UUID
    language_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
