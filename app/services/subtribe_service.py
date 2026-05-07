import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subtribe import SubTribe
from app.repositories.subtribe_repository import SubTribeRepository
from app.schemas.subtribe import SubTribeCreate, SubTribeUpdate,SubTribeData


class BaseSubTribeService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: SubTribeCreate) -> SubTribe: ...

    @abstractmethod
    async def get(self, subtribe_id: uuid.UUID) -> SubTribe: ...

    @abstractmethod
    async def list(self, limit: int, offset: int, tribe_id: Optional[uuid.UUID] = None) -> tuple[list[SubTribe], int]: ...

    @abstractmethod
    async def update(self, subtribe_id: uuid.UUID, data: SubTribeUpdate) -> SubTribe: ...

    @abstractmethod
    async def delete(self, subtribe_id: uuid.UUID) -> None: ...


class SubTribeService(BaseSubTribeService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = SubTribeRepository(db)

    async def create(self, data: SubTribeCreate) -> SubTribe:
        if await self.repo.get_by_name_and_tribe(data.name, data.tribe_id):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"A subtribe named '{data.name}' already exists under this tribe.",
            )
        subtribe = await self.repo.create(data.model_dump())
        return {
            "message": "SubTribe created successfully.",
            "data": SubTribeData(**subtribe.__dict__)
        }

    async def get(self, subtribe_id: uuid.UUID) -> SubTribe:
        subtribe = await self.repo.get_by_id(subtribe_id)
        if not subtribe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SubTribe not found.")
        return subtribe

    async def list(
        self, limit: int = 20, offset: int = 0, tribe_id: Optional[uuid.UUID] = None
    ) -> tuple[list[SubTribe], int]:
        return await self.repo.get_all(limit, offset, tribe_id=tribe_id)

    async def update(self, subtribe_id: uuid.UUID, data: SubTribeUpdate) -> SubTribe:
        subtribe = await self.get(subtribe_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(subtribe, field, value)
        return await self.repo.save(subtribe)

    async def delete(self, subtribe_id: uuid.UUID) -> None:
        subtribe = await self.get(subtribe_id)
        await self.repo.delete(subtribe)
