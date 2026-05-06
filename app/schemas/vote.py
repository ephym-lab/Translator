import uuid
from datetime import datetime
from pydantic import BaseModel

from app.models.response_vote import VoteEnum


class VoteCreate(BaseModel):
    response_id: uuid.UUID
    vote: VoteEnum


class VoteResponse(BaseModel):
    id: uuid.UUID
    vote: VoteEnum
    user_id: uuid.UUID
    response_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
