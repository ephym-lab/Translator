import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# Session Schemas

class ChatSessionCreate(BaseModel):
    """
    Body sent when a user opens a new chat session with another user.
    Language fields are optional — if omitted, the backend will automatically
    use each user's primary registered language (or 'english' as fallback).
    """
    recipient_id: uuid.UUID
    initiator_language: Optional[str] = None  # auto-derived from initiator's profile if None
    recipient_language: Optional[str] = None  # auto-derived from recipient's profile if None


class ChatSessionUpdate(BaseModel):
    """Allows either participant to update their preferred language."""
    initiator_language: Optional[str] = None
    recipient_language: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    initiator_id: uuid.UUID
    recipient_id: uuid.UUID
    initiator_language: str
    recipient_language: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Message Schemas

class SendMessageRequest(BaseModel):
    """
    Body for sending a message.
    - source_lang: the language the sender wrote in (required).
    - target_lang: the language the recipient should receive (optional).
      If omitted, falls back to the recipient's preferred language stored in the session.
      The frontend can populate this from GET /api/v1/users/{id}/languages.
    """
    text: str
    source_lang: str
    target_lang: Optional[str] = None  # explicit override; fallback = session preference


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    sender_id: uuid.UUID
    original_text: str
    source_language: str
    target_language: str
    translated_text: Optional[str] = None
    is_translated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionWithMessages(BaseModel):
    """Session + all its messages — returned when opening / fetching a session."""
    session: ChatSessionResponse
    messages: List[ChatMessageResponse] = []

    model_config = {"from_attributes": True}
