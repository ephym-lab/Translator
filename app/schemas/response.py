import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


from app.schemas.language import LanguageData


class ResponseCreate(BaseModel):
    response_text: str
    dataset_id: uuid.UUID
    language_id: uuid.UUID
    category_id: uuid.UUID


class ResponseUpdate(BaseModel):
    response_text: str


class ResponseSchema(BaseModel):
    id: uuid.UUID
    response_text: str
    response_date: datetime
    is_accepted: bool
    user_id: Optional[uuid.UUID] = None
    dataset_id: uuid.UUID
    language_id: uuid.UUID
    category_id: uuid.UUID
    is_ai_generated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AIResponseItem(BaseModel):
    id: uuid.UUID
    response_text: str
    language: LanguageData
    is_ai_generated: bool
    acceptance_count: int
    rejection_count: int

    model_config = {"from_attributes": True}
