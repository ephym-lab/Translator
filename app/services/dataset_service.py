import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unclean_dataset import UncleanDataset
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.dataset import DatasetCreate, DatasetUpdate


class BaseDatasetService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: DatasetCreate) -> UncleanDataset: ...

    @abstractmethod
    async def get(self, dataset_id: uuid.UUID) -> UncleanDataset: ...

    @abstractmethod
    async def list(self, limit: int, offset: int) -> tuple[list[UncleanDataset], int]: ...

    @abstractmethod
    async def update(self, dataset_id: uuid.UUID, data: DatasetUpdate) -> UncleanDataset: ...

    @abstractmethod
    async def delete(self, dataset_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def recalculate_percentage(self, dataset_id: uuid.UUID) -> None: ...


class DatasetService(BaseDatasetService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = DatasetRepository(db)
        self.category_repo = CategoryRepository(db)

    async def create(self, data: DatasetCreate) -> UncleanDataset:
        if not data.category_ids:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "At least one category is required.")
        
        # Validate categories
        categories = await self.category_repo.get_by_ids(data.category_ids)
        if len(categories) != len(data.category_ids):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "One or more categories do not exist.")
            
        dataset_data = data.model_dump()
        category_ids = dataset_data.pop("category_ids")
        return await self.repo.create(dataset_data, category_ids)

    async def get(self, dataset_id: uuid.UUID) -> UncleanDataset:
        ds = await self.repo.get_by_id(dataset_id)
        if not ds:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Dataset not found.")
        return ds

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[UncleanDataset], int]:
        return await self.repo.get_all(limit, offset)

    async def update(self, dataset_id: uuid.UUID, data: DatasetUpdate) -> UncleanDataset:
        ds = await self.get(dataset_id)
        update_data = data.model_dump(exclude_unset=True)
        
        category_ids = update_data.pop("category_ids", None)
        if category_ids is not None:
            # Validate categories
            categories = await self.category_repo.get_by_ids(category_ids)
            if len(categories) != len(category_ids):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "One or more categories do not exist.")
            ds.allowed_categories = categories

        for field, value in update_data.items():
            setattr(ds, field, value)
            
        return await self.repo.save(ds)

    async def delete(self, dataset_id: uuid.UUID) -> None:
        ds = await self.get(dataset_id)
        await self.repo.delete(ds)

    async def recalculate_percentage(self, dataset_id: uuid.UUID) -> None:
        """
        Business rule: recompute response_percentage and set is_clean=True if >= 80%.
        Called by VoteService after a response is auto-accepted.
        """
        total = await self.repo.count_responses(dataset_id)
        accepted = await self.repo.count_accepted_responses(dataset_id)
        pct = round((accepted / total * 100), 2) if total > 0 else 0.0

        ds = await self.get(dataset_id)
        ds.response_percentage = pct
        ds.is_clean = pct >= 80.0
        await self.repo.save(ds)
