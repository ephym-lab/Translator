import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


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
    user_id: uuid.UUID
    dataset_id: uuid.UUID
    language_id: uuid.UUID
    category_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
