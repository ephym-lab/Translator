import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language import Language


class BaseLanguageRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, language_id: uuid.UUID) -> Language | None: ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Language | None: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> tuple[list[Language], int]: ...

    @abstractmethod
    async def create(self, data: dict) -> Language: ...

    @abstractmethod
    async def save(self, language: Language) -> Language: ...

    @abstractmethod
    async def delete(self, language: Language) -> None: ...


class LanguageRepository(BaseLanguageRepository):
    """All Language DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, language_id: uuid.UUID) -> Language | None:
        try:
            result = await self.db.execute(select(Language).where(Language.id == language_id))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch language") from e

    async def get_by_code(self, code: str) -> Language | None:
        try:
            result = await self.db.execute(select(Language).where(Language.code == code))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch language") from e

    async def get_all(self, limit: int, offset: int) -> tuple[list[Language], int]:
        try:
            total = (await self.db.execute(select(func.count(Language.id)))).scalar()
            result = await self.db.execute(select(Language).limit(limit).offset(offset))
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list languages") from e

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

