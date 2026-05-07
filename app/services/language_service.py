import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.language import Language
from app.repositories.language_repository import LanguageRepository
from app.schemas.language import LanguageCreate, LanguageUpdate, LanguageResponse


class BaseLanguageService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: LanguageCreate) -> Language: ...

    @abstractmethod
    async def get(self, language_id: uuid.UUID) -> Language: ...

    @abstractmethod
    async def listall(self, limit: int, offset: int, subtribe_id: Optional[uuid.UUID] = None) -> tuple[list[Language], int]: ...

    @abstractmethod
    async def update(self, language_id: uuid.UUID, data: LanguageUpdate) -> Language: ...

    @abstractmethod
    async def delete(self, language_id: uuid.UUID) -> None: ...


class LanguageService(BaseLanguageService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = LanguageRepository(db)

    async def create(self, data: LanguageCreate) -> Language:
        if await self.repo.get_by_name(data.name):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"A language named '{data.name}' already exists.")
        if await self.repo.get_by_code(data.code):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Language code '{data.code}' already exists.")
        lang = await self.repo.create(data.model_dump())
        return LanguageResponse(message="Language created successfully.", data=lang)

    async def get(self, language_id: uuid.UUID) -> Language:
        lang = await self.repo.get_by_id(language_id)
        if not lang:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Language not found.")
        return lang

    async def listall(
        self, limit: int = 20, offset: int = 0, subtribe_id: Optional[uuid.UUID] = None
    ) -> tuple[list[Language], int]:
        return await self.repo.get_all(limit, offset, subtribe_id=subtribe_id)

    async def update(self, language_id: uuid.UUID, data: LanguageUpdate) -> Language:
        lang = await self.get(language_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lang, field, value)
        return await self.repo.save(lang)

    async def delete(self, language_id: uuid.UUID) -> None:
        lang = await self.get(language_id)
        await self.repo.delete(lang)
