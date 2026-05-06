import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subtribe import SubTribe


class BaseSubTribeRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, subtribe_id: uuid.UUID) -> SubTribe | None: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> tuple[list[SubTribe], int]: ...

    @abstractmethod
    async def create(self, data: dict) -> SubTribe: ...

    @abstractmethod
    async def save(self, subtribe: SubTribe) -> SubTribe: ...

    @abstractmethod
    async def delete(self, subtribe: SubTribe) -> None: ...


class SubTribeRepository(BaseSubTribeRepository):
    """All SubTribe DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, subtribe_id: uuid.UUID) -> SubTribe | None:
        try:
            result = await self.db.execute(select(SubTribe).where(SubTribe.id == subtribe_id))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch subtribe") from e

    async def get_all(self, limit: int, offset: int) -> tuple[list[SubTribe], int]:
        try:
            total = (await self.db.execute(select(func.count(SubTribe.id)))).scalar()
            result = await self.db.execute(select(SubTribe).limit(limit).offset(offset))
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list subtribes") from e

    async def create(self, data: dict) -> SubTribe:
        try:
            subtribe = SubTribe(id=uuid.uuid4(), **data)
            self.db.add(subtribe)
            await self.db.commit()
            await self.db.refresh(subtribe)
            return subtribe
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to create subtribe") from e

    async def save(self, subtribe: SubTribe) -> SubTribe:
        try:
            await self.db.commit()
            await self.db.refresh(subtribe)
            return subtribe
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to update subtribe") from e

    async def delete(self, subtribe: SubTribe) -> None:
        try:
            await self.db.delete(subtribe)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to delete subtribe") from e

