import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response import Response
from app.models.unclean_dataset import UncleanDataset
from app.repositories.response_repository import ResponseRepository
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.user_dataset_session_repository import UserDatasetSessionRepository
from app.repositories.user_language_repository import UserLanguageRepository
from app.schemas.response import ResponseCreate, ResponseUpdate
from app.models.response_vote import VoteEnum


class BaseResponseService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def submit(self, user_id: uuid.UUID, data: ResponseCreate) -> Response: ...

    @abstractmethod
    async def get(self, response_id: uuid.UUID) -> Response: ...

    @abstractmethod
    async def list_by_dataset(
        self, dataset_id: uuid.UUID, limit: int, offset: int,
        language_id: Optional[uuid.UUID] = None,
        is_ai_generated: Optional[bool] = None,
        vote_type: Optional[VoteEnum] = None,
    ) -> tuple[list[Response], int]: ...

    @abstractmethod
    async def list_all(
        self, limit: int, offset: int, language_id: Optional[uuid.UUID] = None, is_ai_generated: Optional[bool] = None, vote_type: Optional[VoteEnum] = None
    ) -> tuple[list[Response], int]: ...

    @abstractmethod
    async def update(self, response_id: uuid.UUID, user_id: uuid.UUID, data: ResponseUpdate) -> Response: ...

    @abstractmethod
    async def delete(self, response_id: uuid.UUID, user_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def next_dataset(self, user_id: uuid.UUID, language_id: uuid.UUID, category_id: Optional[uuid.UUID] = None) -> UncleanDataset: ...


class ResponseService(BaseResponseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = ResponseRepository(db)
        self.session_repo = UserDatasetSessionRepository(db)
        self.ul_repo = UserLanguageRepository(db)
        self.dataset_repo = DatasetRepository(db)

    # ─── Helpers ─────────────────────────────────────────────────────────────

    async def _validate_user_language(self, user_id: uuid.UUID, language_id: uuid.UUID) -> None:
        """Raise 403 if the language is not in the user's registered languages."""
        user_langs = await self.ul_repo.get_user_languages(user_id)
        user_lang_ids = {lang.id for lang in user_langs}
        if language_id not in user_lang_ids:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "You can only work in a language you have registered.",
            )

    # ─── Endpoints ───────────────────────────────────────────────────────────

    async def next_dataset(self, user_id: uuid.UUID, language_id: uuid.UUID, category_id: Optional[uuid.UUID] = None) -> UncleanDataset:
        """Return the next unseen dataset for this user + language, recording the session."""
        await self._validate_user_language(user_id, language_id)

        dataset = await self.session_repo.next_unseen(user_id, language_id, category_id=category_id)
        if not dataset:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "No more datasets available for this language. Great work!",
            )

        await self.session_repo.record_session(user_id, dataset.id, language_id)
        return dataset

    async def submit(self, user_id: uuid.UUID, data: ResponseCreate) -> Response:
        # 1. Validate the language is registered for this user
        await self._validate_user_language(user_id, data.language_id)

        # 2. Prevent duplicate response (user + dataset + language)
        existing = await self.repo.get_by_user_dataset_language(user_id, data.dataset_id, data.language_id)
        if existing:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "You have already submitted a response for this dataset in this language.",
            )

        # 3. Validate category_id is allowed for the given dataset
        dataset = await self.dataset_repo.get_by_id(data.dataset_id)
        if not dataset:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Dataset not found.")
        
        allowed_category_ids = {cat.id for cat in dataset.allowed_categories}
        if data.category_id not in allowed_category_ids:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "This category is not allowed for this dataset",
            )

        response = Response(
            id=uuid.uuid4(),
            response_text=data.response_text,
            dataset_id=data.dataset_id,
            language_id=data.language_id,
            category_id=data.category_id,
            user_id=user_id,
        )
        return await self.repo.create(response)

    async def get(self, response_id: uuid.UUID) -> Response:
        resp = await self.repo.get_by_id(response_id)
        if not resp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Response not found.")
        return resp

    async def list_by_dataset(
        self, dataset_id: uuid.UUID, limit: int = 20, offset: int = 0,
        language_id: Optional[uuid.UUID] = None,
        is_ai_generated: Optional[bool] = None,
        vote_type: Optional[VoteEnum] = None,
    ) -> tuple[list[Response], int]:
        return await self.repo.get_all_for_dataset(dataset_id, limit, offset, language_id=language_id, is_ai_generated=is_ai_generated, vote_type=vote_type)

    async def list_all(
        self, limit: int = 20, offset: int = 0, language_id: Optional[uuid.UUID] = None, is_ai_generated: Optional[bool] = None, vote_type: Optional[VoteEnum] = None
    ) -> tuple[list[Response], int]:
        return await self.repo.get_all(limit, offset, language_id=language_id, is_ai_generated=is_ai_generated, vote_type=vote_type)

    async def update(self, response_id: uuid.UUID, user_id: uuid.UUID, data: ResponseUpdate) -> Response:
        resp = await self.get(response_id)
        if resp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot edit another user's response.")
        resp.response_text = data.response_text
        return await self.repo.save(resp)

    async def delete(self, response_id: uuid.UUID, user_id: uuid.UUID) -> None:
        resp = await self.get(response_id)
        if resp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot delete another user's response.")
        await self.repo.delete(resp)
