import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tribe import Tribe
from app.repositories.tribe_repository import TribeRepository
from app.schemas.tribe import TribeCreate, TribeUpdate, TribeResponse


class BaseTribeService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: TribeCreate) -> Tribe: ...

    @abstractmethod
    async def get(self, tribe_id: uuid.UUID) -> Tribe: ...

    @abstractmethod
    async def list(self, limit: int, offset: int) -> tuple[list[Tribe], int]: ...

    @abstractmethod
    async def update(self, tribe_id: uuid.UUID, data: TribeUpdate) -> Tribe: ...

    @abstractmethod
    async def delete(self, tribe_id: uuid.UUID) -> None: ...


class TribeService(BaseTribeService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = TribeRepository(db)

    async def create(self, data: TribeCreate) -> Tribe:
        if await self.repo.get_by_name(data.name):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"A tribe named '{data.name}' already exists.")
        tribe = await self.repo.create(data.model_dump())
        return TribeResponse(message="Tribe created successfully", data=tribe)


    async def get(self, tribe_id: uuid.UUID) -> Tribe:
        tribe = await self.repo.get_by_id(tribe_id)
        if not tribe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tribe not found.")
        return tribe

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Tribe], int]:
        return await self.repo.get_all(limit, offset)

    async def update(self, tribe_id: uuid.UUID, data: TribeUpdate) -> Tribe:
        tribe = await self.get(tribe_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(tribe, field, value)
        return await self.repo.save(tribe)

    async def delete(self, tribe_id: uuid.UUID) -> None:
        tribe = await self.get(tribe_id)
        await self.repo.delete(tribe)
