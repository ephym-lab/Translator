import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_dataset_session import UserDatasetSession
from app.models.response import Response
from app.models.unclean_dataset import UncleanDataset


class BaseUserDatasetSessionRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def has_seen(self, user_id: uuid.UUID, dataset_id: uuid.UUID, language_id: uuid.UUID) -> bool: ...

    @abstractmethod
    async def record_session(self, user_id: uuid.UUID, dataset_id: uuid.UUID, language_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def next_unseen(self, user_id: uuid.UUID, language_id: uuid.UUID) -> UncleanDataset | None: ...


class UserDatasetSessionRepository(BaseUserDatasetSessionRepository):
    """Tracks which datasets a user has been served per language."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def has_seen(self, user_id: uuid.UUID, dataset_id: uuid.UUID, language_id: uuid.UUID) -> bool:
        try:
            result = await self.db.execute(
                select(exists().where(
                    UserDatasetSession.user_id == user_id,
                    UserDatasetSession.dataset_id == dataset_id,
                    UserDatasetSession.language_id == language_id,
                ))
            )
            return result.scalar()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to check session") from e

    async def record_session(self, user_id: uuid.UUID, dataset_id: uuid.UUID, language_id: uuid.UUID) -> None:
        try:
            session = UserDatasetSession(
                id=uuid.uuid4(),
                user_id=user_id,
                dataset_id=dataset_id,
                language_id=language_id,
            )
            self.db.add(session)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to record session") from e

    async def next_unseen(self, user_id: uuid.UUID, language_id: uuid.UUID) -> UncleanDataset | None:
        """Return the next dataset not yet seen by this user in this language, oldest first."""
        try:
            # Subquery: dataset_ids already served to this user in this language
            seen_subq = (
                select(UserDatasetSession.dataset_id)
                .where(
                    UserDatasetSession.user_id == user_id,
                    UserDatasetSession.language_id == language_id,
                )
                .scalar_subquery()
            )
            result = await self.db.execute(
                select(UncleanDataset)
                .where(UncleanDataset.id.not_in(seen_subq))
                .order_by(UncleanDataset.created_at.asc())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch next dataset") from e
