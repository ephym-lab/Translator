import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tribe import Tribe


class BaseTribeRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, tribe_id: uuid.UUID) -> Tribe | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Tribe | None: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> tuple[list[Tribe], int]: ...

    @abstractmethod
    async def create(self, data: dict) -> Tribe: ...

    @abstractmethod
    async def save(self, tribe: Tribe) -> Tribe: ...

    @abstractmethod
    async def delete(self, tribe: Tribe) -> None: ...


class TribeRepository(BaseTribeRepository):
    """All Tribe DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, tribe_id: uuid.UUID) -> Tribe | None:
        try:
            result = await self.db.execute(select(Tribe).where(Tribe.id == tribe_id))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch tribe") from e

    async def get_by_name(self, name: str) -> Tribe | None:
        try:
            result = await self.db.execute(select(Tribe).where(Tribe.name == name))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch tribe") from e

    async def get_all(self, limit: int, offset: int) -> tuple[list[Tribe], int]:
        try:
            total = (await self.db.execute(select(func.count(Tribe.id)))).scalar()
            result = await self.db.execute(select(Tribe).limit(limit).offset(offset))
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list tribes") from e

    async def create(self, data: dict) -> Tribe:
        try:
            tribe = Tribe(id=uuid.uuid4(), **data)
            self.db.add(tribe)
            await self.db.commit()
            await self.db.refresh(tribe)
            return tribe
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to create tribe") from e

    async def save(self, tribe: Tribe) -> Tribe:
        try:
            await self.db.commit()
            await self.db.refresh(tribe)
            return tribe
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to update tribe") from e

    async def delete(self, tribe: Tribe) -> None:
        try:
            await self.db.delete(tribe)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to delete tribe") from e

