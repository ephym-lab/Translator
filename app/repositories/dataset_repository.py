import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.unclean_dataset import UncleanDataset
from app.models.response import Response


class BaseDatasetRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, dataset_id: uuid.UUID) -> UncleanDataset | None: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> tuple[list[UncleanDataset], int]: ...

    @abstractmethod
    async def create(self, data: dict) -> UncleanDataset: ...

    @abstractmethod
    async def save(self, dataset: UncleanDataset) -> UncleanDataset: ...

    @abstractmethod
    async def delete(self, dataset: UncleanDataset) -> None: ...

    @abstractmethod
    async def count_responses(self, dataset_id: uuid.UUID) -> int: ...

    @abstractmethod
    async def count_accepted_responses(self, dataset_id: uuid.UUID) -> int: ...


class DatasetRepository(BaseDatasetRepository):
    """All UncleanDataset DB operations including response count queries."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, dataset_id: uuid.UUID) -> UncleanDataset | None:
        try:
            result = await self.db.execute(
                select(UncleanDataset).where(UncleanDataset.id == dataset_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch dataset") from e

    async def get_all(self, limit: int, offset: int) -> tuple[list[UncleanDataset], int]:
        try:
            total = (await self.db.execute(select(func.count(UncleanDataset.id)))).scalar()
            result = await self.db.execute(select(UncleanDataset).limit(limit).offset(offset))
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list datasets") from e

    async def create(self, data: dict) -> UncleanDataset:
        try:
            dataset = UncleanDataset(id=uuid.uuid4(), **data)
            self.db.add(dataset)
            await self.db.commit()
            await self.db.refresh(dataset)
            return dataset
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to create dataset") from e

    async def save(self, dataset: UncleanDataset) -> UncleanDataset:
        try:
            await self.db.commit()
            await self.db.refresh(dataset)
            return dataset
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to update dataset") from e

    async def delete(self, dataset: UncleanDataset) -> None:
        try:
            await self.db.delete(dataset)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to delete dataset") from e

    async def count_responses(self, dataset_id: uuid.UUID) -> int:
        try:
            result = await self.db.execute(
                select(func.count(Response.id)).where(Response.dataset_id == dataset_id)
            )
            return result.scalar() or 0
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to count responses") from e

    async def count_accepted_responses(self, dataset_id: uuid.UUID) -> int:
        try:
            result = await self.db.execute(
                select(func.count(Response.id)).where(
                    and_(Response.dataset_id == dataset_id, Response.is_accepted.is_(True))
                )
            )
            return result.scalar() or 0
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to count accepted responses") from e

