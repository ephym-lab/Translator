import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subtribe import SubTribe


class BaseSubTribeRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, subtribe_id: uuid.UUID) -> Optional[SubTribe]: ...

    @abstractmethod
    async def get_by_name_and_tribe(self, name: str, tribe_id: uuid.UUID) -> Optional[SubTribe]: ...

    @abstractmethod
    async def get_all(
        self, limit: int, offset: int, tribe_id: Optional[uuid.UUID] = None
    ) -> tuple[list[SubTribe], int]: ...

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

    async def get_by_id(self, subtribe_id: uuid.UUID) -> Optional[SubTribe]:
        try:
            result = await self.db.execute(select(SubTribe).where(SubTribe.id == subtribe_id))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch subtribe") from e

    async def get_by_name_and_tribe(self, name: str, tribe_id: uuid.UUID) -> Optional[SubTribe]:
        try:
            result = await self.db.execute(
                select(SubTribe).where(SubTribe.name == name, SubTribe.tribe_id == tribe_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch subtribe") from e

    async def get_all(
        self, limit: int, offset: int, tribe_id: Optional[uuid.UUID] = None
    ) -> tuple[list[SubTribe], int]:
        try:
            query = select(SubTribe)
            count_query = select(func.count(SubTribe.id))
            if tribe_id:
                query = query.where(SubTribe.tribe_id == tribe_id)
                count_query = count_query.where(SubTribe.tribe_id == tribe_id)
            total = (await self.db.execute(count_query)).scalar()
            result = await self.db.execute(query.limit(limit).offset(offset))
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

    #get subtribes in a tribe
    async def get_by_tribe_id(self, tribe_id: uuid.UUID) -> list[SubTribe]:
        try:
            result = await self.db.execute(
                select(SubTribe).where(SubTribe.tribe_id == tribe_id)
            )
            return list(result.scalars().all())
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch subtribes") from e
