import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subtribe import SubTribe
from app.repositories.subtribe_repository import SubTribeRepository
from app.schemas.subtribe import SubTribeCreate, SubTribeUpdate, SubTribeData


class BaseSubTribeService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: SubTribeCreate) -> SubTribeData: ...

    @abstractmethod
    async def get(self, subtribe_id: uuid.UUID) -> SubTribeData: ...

    @abstractmethod
    async def list_all(self, limit: int, offset: int, tribe_id: Optional[uuid.UUID] = None) -> tuple[list[SubTribeData], int]: ...

    @abstractmethod
    async def update(self, subtribe_id: uuid.UUID, data: SubTribeUpdate) -> SubTribeData: ...

    @abstractmethod
    async def delete(self, subtribe_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def get_by_tribe_id(self, tribe_id: uuid.UUID) -> list[SubTribeData]: ...


class SubTribeService(BaseSubTribeService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = SubTribeRepository(db)

    async def create(self, data: SubTribeCreate) -> SubTribeData:
        if await self.repo.get_by_name_and_tribe(data.name, data.tribe_id):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"A subtribe named '{data.name}' already exists under this tribe.",
            )
        subtribe = await self.repo.create(data.model_dump())
        return SubTribeData.model_validate(subtribe)

    async def get(self, subtribe_id: uuid.UUID) -> SubTribeData:
        subtribe = await self.repo.get_by_id(subtribe_id)
        if not subtribe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SubTribe not found.")
        return SubTribeData.model_validate(subtribe)

    async def list_all(
        self, limit: int = 20, offset: int = 0, tribe_id: Optional[uuid.UUID] = None
    ) -> tuple[list[SubTribeData], int]:
        items, total = await self.repo.get_all(limit, offset, tribe_id=tribe_id)
        return [SubTribeData.model_validate(item) for item in items], total

    async def update(self, subtribe_id: uuid.UUID, data: SubTribeUpdate) -> SubTribeData:
        subtribe = await self.repo.get_by_id(subtribe_id)
        if not subtribe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SubTribe not found.")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(subtribe, field, value)
        updated = await self.repo.save(subtribe)
        return SubTribeData.model_validate(updated)

    async def delete(self, subtribe_id: uuid.UUID) -> None:
        subtribe = await self.repo.get_by_id(subtribe_id)
        if not subtribe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SubTribe not found.")
        await self.repo.delete(subtribe)

    async def get_by_tribe_id(self, tribe_id: uuid.UUID) -> list[SubTribeData]:
        subtribes = await self.repo.get_by_tribe_id(tribe_id)
        if not subtribes:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No subtribes found for this tribe.")
        return [SubTribeData.model_validate(s) for s in subtribes]