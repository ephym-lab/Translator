import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subtribe import SubTribe
from app.repositories.subtribe_repository import SubTribeRepository
from app.schemas.subtribe import SubTribeCreate, SubTribeUpdate


class BaseSubTribeService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: SubTribeCreate) -> SubTribe: ...

    @abstractmethod
    async def get(self, subtribe_id: uuid.UUID) -> SubTribe: ...

    @abstractmethod
    async def list(self, limit: int, offset: int) -> tuple[list[SubTribe], int]: ...

    @abstractmethod
    async def update(self, subtribe_id: uuid.UUID, data: SubTribeUpdate) -> SubTribe: ...

    @abstractmethod
    async def delete(self, subtribe_id: uuid.UUID) -> None: ...


class SubTribeService(BaseSubTribeService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = SubTribeRepository(db)

    async def create(self, data: SubTribeCreate) -> SubTribe:
        return await self.repo.create(data.model_dump())

    async def get(self, subtribe_id: uuid.UUID) -> SubTribe:
        subtribe = await self.repo.get_by_id(subtribe_id)
        if not subtribe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SubTribe not found.")
        return subtribe

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[SubTribe], int]:
        return await self.repo.get_all(limit, offset)

    async def update(self, subtribe_id: uuid.UUID, data: SubTribeUpdate) -> SubTribe:
        subtribe = await self.get(subtribe_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(subtribe, field, value)
        return await self.repo.save(subtribe)

    async def delete(self, subtribe_id: uuid.UUID) -> None:
        subtribe = await self.get(subtribe_id)
        await self.repo.delete(subtribe)
