import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.vote import VoteCreate, VoteResponse
from app.schemas.pagination import PaginatedResponse
from app.services.vote_service import VoteService

router = APIRouter(prefix="/votes", tags=["Votes"])


def get_service(db: AsyncSession = Depends(get_db)) -> VoteService:
    return VoteService(db)


@router.post("/", response_model=VoteResponse, status_code=status.HTTP_201_CREATED)
async def cast_vote(
    data: VoteCreate,
    current_user: User = Depends(get_current_user),
    svc: VoteService = Depends(get_service),
):
    """
    Cast an accept/reject vote on a response.
    Triggers acceptance + dataset recalculation when ≥50 votes with ≥80% accept.
    """
    return await svc.cast_vote(current_user.id, data)


@router.get("/response/{response_id}", response_model=PaginatedResponse[VoteResponse])
async def list_votes(
    response_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    svc: VoteService = Depends(get_service),
):
    """List all votes for a specific response (paginated)."""
    items, total = await svc.list_for_response(response_id, limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)
