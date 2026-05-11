import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.unclean_dataset import DatasetLevelEnum
from app.schemas.category import CategoryResponse
from app.schemas.response import AIResponseItem


class DatasetCreate(BaseModel):
    original_text: str
    level: DatasetLevelEnum
    category_ids: list[uuid.UUID]
    language_id: uuid.UUID


class DatasetUpdate(BaseModel):
    original_text: Optional[str] = None
    level: Optional[DatasetLevelEnum] = None
    category_ids: Optional[list[uuid.UUID]] = None
    language_id: Optional[uuid.UUID] = None


class DatasetResponse(BaseModel):
    id: uuid.UUID
    original_text: str
    level: DatasetLevelEnum
    response_percentage: float
    is_clean: bool
    allowed_categories: list[CategoryResponse] = []
    ai_responses: list[AIResponseItem] = []
    language_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
