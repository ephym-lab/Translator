import uuid
from abc import ABC, abstractmethod
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.category import Category
from app.models.dataset_category import DatasetCategory
from app.models.unclean_dataset import UncleanDataset
from app.models.response import Response
from fastapi import HTTPException


class BaseDatasetRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, dataset_id: uuid.UUID) -> UncleanDataset | None: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int, search: str | None = None) -> tuple[list[UncleanDataset], int]: ...

    @abstractmethod
    async def get_datasets_with_ai_responses(self, limit: int, offset: int) -> tuple[list[UncleanDataset], int]: ...

    @abstractmethod
    async def create(self, data: dict, category_ids: list[uuid.UUID]) -> UncleanDataset: ...

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
                select(UncleanDataset)
                .options(
                    selectinload(UncleanDataset.allowed_categories),
                    selectinload(UncleanDataset.responses).selectinload(Response.language),
                    selectinload(UncleanDataset.responses).selectinload(Response.votes),
                )
                .where(UncleanDataset.id == dataset_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch dataset") from e

    async def get_all(self, limit: int, offset: int, search: str | None = None) -> tuple[list[UncleanDataset], int]:
        try:
            query = select(UncleanDataset).options(
                    selectinload(UncleanDataset.allowed_categories),
                    selectinload(UncleanDataset.responses).selectinload(Response.language),
                    selectinload(UncleanDataset.responses).selectinload(Response.votes),
                )
            
            count_query = select(func.count(UncleanDataset.id))
            
            if search:
                query = query.where(UncleanDataset.original_text.ilike(f"%{search}%"))
                count_query = count_query.where(UncleanDataset.original_text.ilike(f"%{search}%"))

            total = (await self.db.execute(count_query)).scalar() or 0
            result = await self.db.execute(
                query.limit(limit).offset(offset)
            )
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list datasets") from e

    async def get_datasets_with_ai_responses(self, limit: int, offset: int) -> tuple[list[UncleanDataset], int]:
        try:
            query = (
                select(UncleanDataset)
                .join(UncleanDataset.responses)
                .where(Response.is_ai_generated == True)
                .options(
                    selectinload(UncleanDataset.allowed_categories),
                    selectinload(UncleanDataset.responses).selectinload(Response.language),
                    selectinload(UncleanDataset.responses).selectinload(Response.votes),
                )
                .distinct()
            )
            count_query = select(func.count(func.distinct(UncleanDataset.id))).join(UncleanDataset.responses).where(Response.is_ai_generated == True)
            
            total = (await self.db.execute(count_query)).scalar() or 0
            result = await self.db.execute(query.limit(limit).offset(offset))
            
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list datasets with ai responses") from e

    async def create(self, data: dict, category_ids: list[uuid.UUID]) -> UncleanDataset:
        try:
            dataset = UncleanDataset(id=uuid.uuid4(), **data)
            self.db.add(dataset)
            await self.db.flush()
            if category_ids:
                for cat_id in category_ids:
                    self.db.add(DatasetCategory(dataset_id=dataset.id, category_id=cat_id))
            await self.db.commit()
            return await self.get_by_id(dataset.id)
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to create dataset") from e

    async def save(self, dataset: UncleanDataset) -> UncleanDataset:
        try:
            await self.db.commit()
            return await self.get_by_id(dataset.id)
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
    

    
    

