import uuid
from abc import ABC, abstractmethod
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.response import Response
from fastapi import HTTPException


class BaseResponseRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, response_id: uuid.UUID) -> Response | None: ...

    @abstractmethod
    async def get_all_for_dataset(
        self, dataset_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Response], int]: ...

    @abstractmethod
    async def create(self, response: Response) -> Response: ...

    @abstractmethod
    async def save(self, response: Response) -> Response: ...

    @abstractmethod
    async def delete(self, response: Response) -> None: ...


class ResponseRepository(BaseResponseRepository):
    """All Response DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, response_id: uuid.UUID) -> Response | None:
        try:
            result = await self.db.execute(select(Response).where(Response.id == response_id))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch response") from e

    async def get_all_for_dataset(
        self, dataset_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Response], int]:
        try:
            total = (
                await self.db.execute(
                    select(func.count(Response.id)).where(Response.dataset_id == dataset_id)
                )
            ).scalar()
            result = await self.db.execute(
                select(Response).where(Response.dataset_id == dataset_id).limit(limit).offset(offset)
            )
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list responses") from e

    async def create(self, response: Response) -> Response:
        try:
            self.db.add(response)
            await self.db.commit()
            await self.db.refresh(response)
            return response
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to create response") from e

    async def save(self, response: Response) -> Response:
        try:
            await self.db.commit()
            await self.db.refresh(response)
            return response
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to update response") from e

    async def delete(self, response: Response) -> None:
        try:
            await self.db.delete(response)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to delete response") from e

