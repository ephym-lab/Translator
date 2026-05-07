import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.language import Language
from app.models.subtribe import SubTribe


class BaseLanguageRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, language_id: uuid.UUID) -> Optional[Language]: ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Language]: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Language]: ...

    @abstractmethod
    async def get_all(
        self, limit: int, offset: int, subtribe_id: Optional[uuid.UUID] = None
    ) -> tuple[list[Language], int]: ...

    @abstractmethod
    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Language]: ...

    @abstractmethod
    async def create(self, data: dict) -> Language: ...

    @abstractmethod
    async def save(self, language: Language) -> Language: ...

    @abstractmethod
    async def delete(self, language: Language) -> None: ...


import logging
logger = logging.getLogger(__name__)


class LanguageRepository(BaseLanguageRepository):
    """All Language DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, language_id: uuid.UUID) -> Optional[Language]:
        try:
            result = await self.db.execute(
                select(Language)
                .options(selectinload(Language.subtribe).selectinload(SubTribe.tribe))
                .where(Language.id == language_id)
            )
            lang = result.scalar_one_or_none()
            logger.info("Fetched language by id '%s': %s", language_id, lang)
            return lang
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: failed to fetch language — {e}") from e

    async def get_by_code(self, code: str) -> Optional[Language]:
        try:
            result = await self.db.execute(select(Language).where(Language.code == code))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: failed to fetch language — {e}") from e

    async def get_by_name(self, name: str) -> Optional[Language]:
        try:
            result = await self.db.execute(select(Language).where(Language.name == name))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: failed to fetch language — {e}") from e

    async def get_all(
        self, limit: int, offset: int, subtribe_id: Optional[uuid.UUID] = None
    ) -> tuple[list[Language], int]:
        try:
            query = select(Language).options(
                selectinload(Language.subtribe).selectinload(SubTribe.tribe)
            )
            count_query = select(func.count(Language.id))
            if subtribe_id:
                query = query.where(Language.subtribe_id == subtribe_id)
                count_query = count_query.where(Language.subtribe_id == subtribe_id)
            total = (await self.db.execute(count_query)).scalar()
            result = await self.db.execute(query.limit(limit).offset(offset))
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list languages") from e

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Language]:
        try:
            result = await self.db.execute(
                select(Language)
                .options(selectinload(Language.subtribe).selectinload(SubTribe.tribe))
                .where(Language.id.in_(ids))
            )
            return list(result.scalars().all())
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch languages") from e

    async def create(self, data: dict) -> Language:
        try:
            lang = Language(id=uuid.uuid4(), **data)
            self.db.add(lang)
            await self.db.commit()
            await self.db.refresh(lang)
            return lang
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to create language") from e

    async def save(self, language: Language) -> Language:
        try:
            await self.db.commit()
            await self.db.refresh(language)
            return language
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to update language") from e

    async def delete(self, language: Language) -> None:
        try:
            await self.db.delete(language)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to delete language") from e
