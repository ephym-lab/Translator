import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.subtribe import SubTribeCreate, SubTribeResponse, SubTribeUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.subtribe_service import SubTribeService

router = APIRouter(prefix="/subtribes", tags=["SubTribes"])


def get_service(db: AsyncSession = Depends(get_db)) -> SubTribeService:
    return SubTribeService(db)


@router.post("/", response_model=SubTribeResponse, status_code=status.HTTP_201_CREATED)
async def create_subtribe(
    data: SubTribeCreate,
    svc: SubTribeService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.create(data)


@router.get("/", response_model=PaginatedResponse[SubTribeResponse])
async def list_subtribes(limit: int = 20, offset: int = 0, svc: SubTribeService = Depends(get_service)):
    items, total = await svc.list(limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{subtribe_id}", response_model=SubTribeResponse)
async def get_subtribe(subtribe_id: uuid.UUID, svc: SubTribeService = Depends(get_service)):
    return await svc.get(subtribe_id)


@router.patch("/{subtribe_id}", response_model=SubTribeResponse)
async def update_subtribe(
    subtribe_id: uuid.UUID,
    data: SubTribeUpdate,
    svc: SubTribeService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.update(subtribe_id, data)


@router.delete("/{subtribe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtribe(
    subtribe_id: uuid.UUID,
    svc: SubTribeService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    await svc.delete(subtribe_id)
