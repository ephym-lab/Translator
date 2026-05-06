import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class BaseCategoryService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create(self, data: CategoryCreate) -> Category: ...

    @abstractmethod
    async def get(self, category_id: uuid.UUID) -> Category: ...

    @abstractmethod
    async def list(self, limit: int, offset: int) -> tuple[list[Category], int]: ...

    @abstractmethod
    async def update(self, category_id: uuid.UUID, data: CategoryUpdate) -> Category: ...

    @abstractmethod
    async def delete(self, category_id: uuid.UUID) -> None: ...


class CategoryService(BaseCategoryService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = CategoryRepository(db)

    async def create(self, data: CategoryCreate) -> Category:
        # Business rule: category names must be unique
        if await self.repo.get_by_name(data.name):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Category '{data.name}' already exists.")
        return await self.repo.create(data.model_dump())

    async def get(self, category_id: uuid.UUID) -> Category:
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found.")
        return cat

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Category], int]:
        return await self.repo.get_all(limit, offset)

    async def update(self, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
        cat = await self.get(category_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cat, field, value)
        return await self.repo.save(cat)

    async def delete(self, category_id: uuid.UUID) -> None:
        cat = await self.get(category_id)
        await self.repo.delete(cat)
