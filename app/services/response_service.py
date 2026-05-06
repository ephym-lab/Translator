import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response import Response
from app.repositories.response_repository import ResponseRepository
from app.schemas.response import ResponseCreate, ResponseUpdate


class BaseResponseService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def submit(self, user_id: uuid.UUID, data: ResponseCreate) -> Response: ...

    @abstractmethod
    async def get(self, response_id: uuid.UUID) -> Response: ...

    @abstractmethod
    async def list_by_dataset(
        self, dataset_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Response], int]: ...

    @abstractmethod
    async def update(self, response_id: uuid.UUID, user_id: uuid.UUID, data: ResponseUpdate) -> Response: ...

    @abstractmethod
    async def delete(self, response_id: uuid.UUID, user_id: uuid.UUID) -> None: ...


class ResponseService(BaseResponseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = ResponseRepository(db)

    async def submit(self, user_id: uuid.UUID, data: ResponseCreate) -> Response:
        response = Response(
            id=uuid.uuid4(),
            response_text=data.response_text,
            dataset_id=data.dataset_id,
            user_id=user_id,
        )
        return await self.repo.create(response)

    async def get(self, response_id: uuid.UUID) -> Response:
        resp = await self.repo.get_by_id(response_id)
        if not resp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Response not found.")
        return resp

    async def list_by_dataset(
        self, dataset_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[Response], int]:
        return await self.repo.get_all_for_dataset(dataset_id, limit, offset)

    async def update(self, response_id: uuid.UUID, user_id: uuid.UUID, data: ResponseUpdate) -> Response:
        resp = await self.get(response_id)
        # Business rule: only the author can edit
        if resp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot edit another user's response.")
        resp.response_text = data.response_text
        return await self.repo.save(resp)

    async def delete(self, response_id: uuid.UUID, user_id: uuid.UUID) -> None:
        resp = await self.get(response_id)
        # Business rule: only the author can delete
        if resp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot delete another user's response.")
        await self.repo.delete(resp)

    #get all responses in general
    async def list_all(self, limit: int = 20, offset: int = 0) -> tuple[list[Response], int]:
        return await self.repo.get_all(limit, offset)
