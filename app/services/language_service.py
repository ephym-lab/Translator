import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language import Language
from app.repositories.language_repository import LanguageRepository
from app.schemas.language import LanguageCreate, LanguageUpdate


class BaseLanguageService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: LanguageCreate) -> Language: ...

    @abstractmethod
    async def get(self, language_id: uuid.UUID) -> Language: ...

    @abstractmethod
    async def list(self, limit: int, offset: int) -> tuple[list[Language], int]: ...

    @abstractmethod
    async def update(self, language_id: uuid.UUID, data: LanguageUpdate) -> Language: ...

    @abstractmethod
    async def delete(self, language_id: uuid.UUID) -> None: ...


class LanguageService(BaseLanguageService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = LanguageRepository(db)

    async def create(self, data: LanguageCreate) -> Language:
        # Business rule: language codes must be unique
        if await self.repo.get_by_code(data.code):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Language code '{data.code}' already exists.")
        return await self.repo.create(data.model_dump())

    async def get(self, language_id: uuid.UUID) -> Language:
        lang = await self.repo.get_by_id(language_id)
        if not lang:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Language not found.")
        return lang

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Language], int]:
        return await self.repo.get_all(limit, offset)

    async def update(self, language_id: uuid.UUID, data: LanguageUpdate) -> Language:
        lang = await self.get(language_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lang, field, value)
        return await self.repo.save(lang)

    async def delete(self, language_id: uuid.UUID) -> None:
        lang = await self.get(language_id)
        await self.repo.delete(lang)
