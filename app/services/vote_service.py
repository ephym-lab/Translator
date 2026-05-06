import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response import Response
from app.models.response_vote import ResponseVote, VoteEnum
from app.repositories.vote_repository import VoteRepository
from app.repositories.response_repository import ResponseRepository
from app.services.dataset_service import DatasetService
from app.schemas.vote import VoteCreate

VOTE_THRESHOLD = 50
ACCEPT_RATIO = 0.80


class BaseVoteService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def cast_vote(self, user_id: uuid.UUID, data: VoteCreate) -> ResponseVote: ...

    @abstractmethod
    async def list_for_response(
        self, response_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[ResponseVote], int]: ...


class VoteService(BaseVoteService):
    """
    Business logic for vote casting and the auto-acceptance threshold.

    Rule: >= 50 votes AND >= 80% accept → mark Response.is_accepted = True
          → then call DatasetService.recalculate_percentage()
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = VoteRepository(db)
        self.response_repo = ResponseRepository(db)
        self.dataset_service = DatasetService(db)

    async def cast_vote(self, user_id: uuid.UUID, data: VoteCreate) -> ResponseVote:
        # Verify response exists
        response = await self.response_repo.get_by_id(data.response_id)
        if not response:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Response not found.")

        # Business rule: one vote per user per response
        if await self.repo.get_by_user_and_response(user_id, data.response_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have already voted on this response.")

        vote = ResponseVote(
            id=uuid.uuid4(),
            vote=data.vote,
            user_id=user_id,
            response_id=data.response_id,
        )
        vote = await self.repo.create(vote)  # flush but no commit yet

        # Business rule: evaluate threshold after each vote
        await self._evaluate_threshold(response)
        await self.db.commit()
        await self.db.refresh(vote)
        return vote

    async def _evaluate_threshold(self, response: Response) -> None:
        """
        Check if the response has crossed the acceptance threshold.
        Delegates all counts to VoteRepository, all dataset updates to DatasetService.
        """
        total = await self.repo.count_all_for_response(response.id)
        if total < VOTE_THRESHOLD:
            return

        accepted = await self.repo.count_accepted_for_response(response.id)
        if (accepted / total) >= ACCEPT_RATIO:
            response.is_accepted = True
            await self.db.flush()
            await self.dataset_service.recalculate_percentage(response.dataset_id)

    async def list_for_response(
        self, response_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[ResponseVote], int]:
        return await self.repo.get_all_for_response(response_id, limit, offset)
