import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response import Response


class BaseResponseRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, response_id: uuid.UUID) -> Response | None: ...

    @abstractmethod
    async def get_by_user_dataset_language(
        self, user_id: uuid.UUID, dataset_id: uuid.UUID, language_id: uuid.UUID
    ) -> Response | None: ...

    @abstractmethod
    async def get_all_for_dataset(
        self, dataset_id: uuid.UUID, limit: int, offset: int,
        language_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[Response], int]: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int, language_id: Optional[uuid.UUID] = None) -> tuple[list[Response], int]: ...

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

    async def get_by_user_dataset_language(
        self, user_id: uuid.UUID, dataset_id: uuid.UUID, language_id: uuid.UUID
    ) -> Response | None:
        try:
            result = await self.db.execute(
                select(Response).where(
                    and_(
                        Response.user_id == user_id,
                        Response.dataset_id == dataset_id,
                        Response.language_id == language_id,
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to check duplicate response") from e

    async def get_all_for_dataset(
        self, dataset_id: uuid.UUID, limit: int, offset: int,
        language_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[Response], int]:
        try:
            filters = [Response.dataset_id == dataset_id]
            if language_id:
                filters.append(Response.language_id == language_id)
            total = (await self.db.execute(select(func.count(Response.id)).where(and_(*filters)))).scalar()
            result = await self.db.execute(
                select(Response).where(and_(*filters)).limit(limit).offset(offset)
            )
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list responses") from e

    async def get_all(
        self, limit: int, offset: int, language_id: Optional[uuid.UUID] = None
    ) -> tuple[list[Response], int]:
        try:
            query = select(Response)
            count_q = select(func.count(Response.id))
            if language_id:
                query = query.where(Response.language_id == language_id)
                count_q = count_q.where(Response.language_id == language_id)
            total = (await self.db.execute(count_q)).scalar()
            result = await self.db.execute(query.limit(limit).offset(offset))
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
