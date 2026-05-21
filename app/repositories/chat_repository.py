import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatSession, ChatMessage, SessionStatusEnum
from app.models.user import User


class ChatRepository:
    """All DB operations for ChatSession and ChatMessage."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Sessions ───────────────────────────────────────────────────────────────

    async def get_session_by_id(self, session_id: uuid.UUID) -> ChatSession | None:
        try:
            result = await self.db.execute(
                select(ChatSession)
                .options(selectinload(ChatSession.messages))
                .where(ChatSession.id == session_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error fetching session: {e}") from e

    async def get_session_between(
        self, user_a: uuid.UUID, user_b: uuid.UUID
    ) -> ChatSession | None:
        """Return the session between two users regardless of who initiated."""
        try:
            result = await self.db.execute(
                select(ChatSession)
                .options(selectinload(ChatSession.messages))
                .where(
                    or_(
                        and_(
                            ChatSession.initiator_id == user_a,
                            ChatSession.recipient_id == user_b,
                        ),
                        and_(
                            ChatSession.initiator_id == user_b,
                            ChatSession.recipient_id == user_a,
                        ),
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error looking up session: {e}") from e

    async def get_sessions_for_user(self, user_id: uuid.UUID) -> list[ChatSession]:
        """Return all sessions where this user is a participant."""
        try:
            result = await self.db.execute(
                select(ChatSession)
                .where(
                    or_(
                        ChatSession.initiator_id == user_id,
                        ChatSession.recipient_id == user_id,
                    )
                )
                .order_by(ChatSession.updated_at.desc())
            )
            return list(result.scalars().all())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error listing sessions: {e}") from e

    async def create_session(self, session: ChatSession) -> ChatSession:
        try:
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            return session
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"DB error creating session: {e}") from e

    async def save_session(self, session: ChatSession) -> ChatSession:
        try:
            await self.db.commit()
            await self.db.refresh(session)
            return session
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"DB error updating session: {e}") from e

    async def get_user_with_languages(self, user_id: uuid.UUID) -> User | None:
        """Fetch a user with their language list eagerly loaded."""
        try:
            from app.models.user_language import UserLanguage
            from app.models.language import Language
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.languages))
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error fetching user: {e}") from e

    # ── Messages ───────────────────────────────────────────────────────────────

    async def get_messages(
        self,
        session_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ChatMessage], int]:
        try:
            from sqlalchemy import func
            total = (
                await self.db.execute(
                    select(func.count(ChatMessage.id)).where(
                        ChatMessage.session_id == session_id
                    )
                )
            ).scalar() or 0

            result = await self.db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error fetching messages: {e}") from e

    async def create_message(self, message: ChatMessage) -> ChatMessage:
        try:
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)
            return message
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"DB error creating message: {e}") from e
