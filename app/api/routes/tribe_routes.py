import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.tribe import TribeCreate, TribeResponse, TribeUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.tribe_service import TribeService

router = APIRouter(prefix="/tribes", tags=["Tribes"])


def get_service(db: AsyncSession = Depends(get_db)) -> TribeService:
    return TribeService(db)


@router.post("/", response_model=TribeResponse, status_code=status.HTTP_201_CREATED)
async def create_tribe(
    data: TribeCreate,
    svc: TribeService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.create(data)


@router.get("/", response_model=PaginatedResponse[TribeResponse])
async def list_tribes(limit: int = 20, offset: int = 0, svc: TribeService = Depends(get_service)):
    items, total = await svc.list(limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{tribe_id}", response_model=TribeResponse)
async def get_tribe(tribe_id: uuid.UUID, svc: TribeService = Depends(get_service)):
    return await svc.get(tribe_id)


@router.patch("/{tribe_id}", response_model=TribeResponse)
async def update_tribe(
    tribe_id: uuid.UUID,
    data: TribeUpdate,
    svc: TribeService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.update(tribe_id, data)


@router.delete("/{tribe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tribe(
    tribe_id: uuid.UUID,
    svc: TribeService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    await svc.delete(tribe_id)
