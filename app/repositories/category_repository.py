import uuid
from abc import ABC, abstractmethod
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category


class BaseCategoryRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, category_id: uuid.UUID) -> Category | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Category | None: ...

    @abstractmethod
    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Category]: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> tuple[list[Category], int]: ...

    @abstractmethod
    async def create(self, data: dict) -> Category: ...

    @abstractmethod
    async def save(self, category: Category) -> Category: ...

    @abstractmethod
    async def delete(self, category: Category) -> None: ...


class CategoryRepository(BaseCategoryRepository):
    """All Category DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        try:
            result = await self.db.execute(select(Category).where(Category.id == category_id))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch category") from e

    async def get_by_name(self, name: str) -> Category | None:
        try:
            result = await self.db.execute(select(Category).where(Category.name == name))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch category") from e

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Category]:
        try:
            result = await self.db.execute(select(Category).where(Category.id.in_(ids)))
            return list(result.scalars().all())
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch categories") from e

    async def get_all(self, limit: int, offset: int) -> tuple[list[Category], int]:
        try:
            total = (await self.db.execute(select(func.count(Category.id)))).scalar()
            result = await self.db.execute(select(Category).limit(limit).offset(offset))
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to list categories") from e

    async def create(self, data: dict) -> Category:
        try:
            cat = Category(id=uuid.uuid4(), **data)
            self.db.add(cat)
            await self.db.commit()
            await self.db.refresh(cat)
            return cat
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create category") from e

    async def save(self, category: Category) -> Category:
        try:
            await self.db.commit()
            await self.db.refresh(category)
            return category
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update category") from e

    async def delete(self, category: Category) -> None:
        try:
            await self.db.delete(category)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete category") from e
