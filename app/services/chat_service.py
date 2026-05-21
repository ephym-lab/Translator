import uuid
import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatSession, ChatMessage, SessionStatusEnum
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatSessionCreate, ChatSessionUpdate, SendMessageRequest
from app.services.TTTService import NLLBTTTService

logger = logging.getLogger(__name__)

# Single shared model instance (lazy-loaded on first use)
_ttt_service = NLLBTTTService()


class ChatService:
    """
    Business logic for the translation-powered chat feature.

    Flow for sending a message:
      1. Verify the session exists and the sender is a participant.
      2. Call TTTService.translate_async(text, source_lang, target_lang).
      3. Persist a ChatMessage with both original + translated text.
    """

    def __init__(self, db: AsyncSession):
        self.repo = ChatRepository(db)

    #Session management

    async def create_session(
        self, initiator: User, data: ChatSessionCreate
    ) -> ChatSession:
        """Open a new chat session. Languages auto-derived from user profiles."""
        if initiator.id == data.recipient_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "You cannot start a chat with yourself."
            )

        existing = await self.repo.get_session_between(initiator.id, data.recipient_id)
        if existing:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "A chat session between these users already exists.",
            )

        # Auto-detect languages from user profiles if not explicitly provided
        initiator_lang = data.initiator_language or self._primary_language(initiator)

        recipient_user = await self.repo.get_user_with_languages(data.recipient_id)
        if not recipient_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Recipient user not found.")
        recipient_lang = data.recipient_language or self._primary_language(recipient_user)

        session = ChatSession(
            id=uuid.uuid4(),
            initiator_id=initiator.id,
            recipient_id=data.recipient_id,
            initiator_language=initiator_lang,
            recipient_language=recipient_lang,
            status=SessionStatusEnum.active,
        )
        return await self.repo.create_session(session)

    async def get_or_open_session(
        self, current_user: User, data: ChatSessionCreate
    ) -> ChatSession:
        """Return existing session or create a new one."""
        existing = await self.repo.get_session_between(
            current_user.id, data.recipient_id
        )
        if existing:
            return existing
        return await self.create_session(current_user, data)

    async def get_session(
        self, session_id: uuid.UUID, current_user: User
    ) -> ChatSession:
        session = await self.repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat session not found.")
        self._assert_participant(session, current_user.id)
        return session

    async def list_my_sessions(self, current_user: User) -> list[ChatSession]:
        return await self.repo.get_sessions_for_user(current_user.id)

    async def update_session_languages(
        self,
        session_id: uuid.UUID,
        current_user: User,
        data: ChatSessionUpdate,
    ) -> ChatSession:
        session = await self.get_session(session_id, current_user)
        if data.initiator_language is not None:
            session.initiator_language = data.initiator_language.lower().strip()
        if data.recipient_language is not None:
            session.recipient_language = data.recipient_language.lower().strip()
        return await self.repo.save_session(session)

    async def close_session(
        self, session_id: uuid.UUID, current_user: User
    ) -> ChatSession:
        session = await self.get_session(session_id, current_user)
        if session.status == SessionStatusEnum.closed:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session is already closed.")
        session.status = SessionStatusEnum.closed
        return await self.repo.save_session(session)

    async def reopen_session(
        self, session_id: uuid.UUID, current_user: User
    ) -> ChatSession:
        session = await self.get_session(session_id, current_user)
        if session.status == SessionStatusEnum.active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session is already active.")
        session.status = SessionStatusEnum.active
        return await self.repo.save_session(session)

    #Messaging

    async def send_message(
        self,
        session_id: uuid.UUID,
        sender: User,
        payload: SendMessageRequest,
    ) -> ChatMessage:
        session = await self.get_session(session_id, sender)

        if session.status == SessionStatusEnum.closed:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "This chat session has been closed.",
            )

        # Determine target language:
        # 1. Use explicit value from request (e.g. picked from dropdown) if provided
        # 2. Otherwise fall back to the session's stored language preference for the recipient
        if payload.target_lang:
            target_lang = payload.target_lang.lower().strip()
        elif sender.id == session.initiator_id:
            target_lang = session.recipient_language  # initiator → recipient's preferred lang
        else:
            target_lang = session.initiator_language  # recipient → initiator's preferred lang

        source_lang = payload.source_lang.lower().strip()

        # Translate the message
        translated_text: str | None = None
        is_translated = False

        try:
            translated_text = await _ttt_service.translate_async(
                text=payload.text,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            is_translated = True
            logger.info(
                f"[Chat] Translated '{payload.text}' "
                f"({source_lang} → {target_lang}): '{translated_text}'"
            )
        except Exception as e:
            logger.warning(
                f"[Chat] Translation failed, storing original text. Error: {e}"
            )
            translated_text = payload.text  # fallback: send original

        message = ChatMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            sender_id=sender.id,
            original_text=payload.text,
            source_language=source_lang,
            target_language=target_lang,
            translated_text=translated_text,
            is_translated=is_translated,
        )
        return await self.repo.create_message(message)

    async def get_messages(
        self,
        session_id: uuid.UUID,
        current_user: User,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ChatMessage], int]:
        session = await self.repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat session not found.")
        self._assert_participant(session, current_user.id)
        return await self.repo.get_messages(session_id, limit, offset)

    #Helpers

    @staticmethod
    def _primary_language(user: User) -> str:
        """
        Returns the user's first registered language name (lowercase),
        or 'english' if they have no languages registered.
        """
        if user.languages:
            return user.languages[0].name.lower().strip()
        return "english"

    @staticmethod
    def _assert_participant(session: ChatSession, user_id: uuid.UUID) -> None:
        if session.initiator_id != user_id and session.recipient_id != user_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "You are not a participant of this chat session.",
            )
