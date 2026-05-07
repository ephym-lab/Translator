import uuid
from abc import ABC, abstractmethod
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user_language import UserLanguage
from app.models.language import Language
from app.models.subtribe import SubTribe


class BaseUserLanguageRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_user_language(self, user_id: uuid.UUID, language_id: uuid.UUID) -> Optional[UserLanguage]: ...

    @abstractmethod
    async def get_user_languages(self, user_id: uuid.UUID) -> list[Language]: ...

    @abstractmethod
    async def add_language(self, user_id: uuid.UUID, language_id: uuid.UUID) -> UserLanguage: ...

    @abstractmethod
    async def remove_language(self, user_id: uuid.UUID, language_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def bulk_add_languages(self, user_id: uuid.UUID, language_ids: list[uuid.UUID]) -> None: ...


class UserLanguageRepository(BaseUserLanguageRepository):
    """All UserLanguage junction table DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_user_language(
        self, user_id: uuid.UUID, language_id: uuid.UUID
    ) -> Optional[UserLanguage]:
        try:
            result = await self.db.execute(
                select(UserLanguage).where(
                    UserLanguage.user_id == user_id,
                    UserLanguage.language_id == language_id,
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch user language") from e

    async def get_user_languages(self, user_id: uuid.UUID) -> list[Language]:
        try:
            result = await self.db.execute(
                select(Language)
                .options(selectinload(Language.subtribe).selectinload(SubTribe.tribe))
                .join(UserLanguage, UserLanguage.language_id == Language.id)
                .where(UserLanguage.user_id == user_id)
            )
            return list(result.scalars().all())
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch user languages") from e

    async def add_language(self, user_id: uuid.UUID, language_id: uuid.UUID) -> UserLanguage:
        try:
            ul = UserLanguage(id=uuid.uuid4(), user_id=user_id, language_id=language_id)
            self.db.add(ul)
            await self.db.commit()
            await self.db.refresh(ul)
            return ul
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to add language") from e

    async def remove_language(self, user_id: uuid.UUID, language_id: uuid.UUID) -> None:
        try:
            await self.db.execute(
                delete(UserLanguage).where(
                    UserLanguage.user_id == user_id,
                    UserLanguage.language_id == language_id,
                )
            )
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to remove language") from e

    async def bulk_add_languages(self, user_id: uuid.UUID, language_ids: list[uuid.UUID]) -> None:
        try:
            entries = [
                UserLanguage(id=uuid.uuid4(), user_id=user_id, language_id=lid)
                for lid in language_ids
            ]
            self.db.add_all(entries)
            # Caller commits (same transaction as user creation)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to bulk add languages") from e
