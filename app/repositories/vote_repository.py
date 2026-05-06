import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response_vote import ResponseVote, VoteEnum


class BaseVoteRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_user_and_response(
        self, user_id: uuid.UUID, response_id: uuid.UUID
    ) -> ResponseVote | None: ...

    @abstractmethod
    async def get_all_for_response(
        self, response_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[ResponseVote], int]: ...

    @abstractmethod
    async def count_all_for_response(self, response_id: uuid.UUID) -> int: ...

    @abstractmethod
    async def count_accepted_for_response(self, response_id: uuid.UUID) -> int: ...

    @abstractmethod
    async def create(self, vote: ResponseVote) -> ResponseVote: ...


class VoteRepository(BaseVoteRepository):
    """All ResponseVote DB operations including threshold count queries."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_user_and_response(
        self, user_id: uuid.UUID, response_id: uuid.UUID
    ) -> ResponseVote | None:
        try:
            result = await self.db.execute(
                select(ResponseVote).where(
                    and_(
                        ResponseVote.user_id == user_id,
                        ResponseVote.response_id == response_id,
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch vote") from e

    async def get_all_for_response(
        self, response_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[ResponseVote], int]:
        total = await self.count_all_for_response(response_id)
        try:
            result = await self.db.execute(
                select(ResponseVote)
                .where(ResponseVote.response_id == response_id)
                .limit(limit)
                .offset(offset)
            )
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list votes") from e

    async def count_all_for_response(self, response_id: uuid.UUID) -> int:
        try:
            result = await self.db.execute(
                select(func.count(ResponseVote.id)).where(ResponseVote.response_id == response_id)
            )
            return result.scalar() or 0
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to count votes") from e

    async def count_accepted_for_response(self, response_id: uuid.UUID) -> int:
        try:
            result = await self.db.execute(
                select(func.count(ResponseVote.id)).where(
                    and_(
                        ResponseVote.response_id == response_id,
                        ResponseVote.vote == VoteEnum.accept,
                    )
                )
            )
            return result.scalar() or 0
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to count accepted votes") from e

    async def create(self, vote: ResponseVote) -> ResponseVote:
        try:
            self.db.add(vote)
            await self.db.flush()
            return vote
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to save vote") from e

