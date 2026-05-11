import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.vote import VoteCreate, VoteResponse
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.services.vote_service import VoteService
from app.models.response_vote import VoteEnum

router = APIRouter(prefix="/votes", tags=["Votes"])


def get_service(db: AsyncSession = Depends(get_db)) -> VoteService:
    return VoteService(db)


@router.post("/", response_model=APIResponse[VoteResponse], status_code=status.HTTP_201_CREATED)
async def cast_vote(
    data: VoteCreate,
    current_user: User = Depends(get_current_user),
    svc: VoteService = Depends(get_service),
):
    """
    Cast an accept/reject vote on a response.
    Triggers acceptance + dataset recalculation when ≥50 votes with ≥80% accept.
    """
    result = await svc.cast_vote(current_user.id, data)
    return APIResponse(success=True, message="Vote cast successfully.", data=result, status=status.HTTP_201_CREATED)

@router.get("/response/{response_id}/count", response_model=APIResponse[dict])
async def get_votes_count(
    response_id: uuid.UUID,
    svc: VoteService = Depends(get_service),
):
    """Get the total, accepted, and rejected votes count for a specific response."""
    result = await svc.get_votes_count(response_id)
    return APIResponse(success=True, message="Votes count retrieved successfully.", data=result, status=status.HTTP_200_OK)
