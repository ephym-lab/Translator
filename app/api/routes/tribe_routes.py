import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.tribe import TribeCreate, TribeResponse, TribeUpdate, TribeData
from app.schemas.pagination import PaginatedResponse, PaginatedData
from app.services.tribe_service import TribeService

router = APIRouter(prefix="/tribes", tags=["Tribes"])


def get_service(db: AsyncSession = Depends(get_db)) -> TribeService:
    return TribeService(db)


@router.post("/", response_model=TribeResponse, status_code=status.HTTP_201_CREATED)
async def create_tribe(
    data: TribeCreate,
    svc: TribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Create a tribe. Admin only."""
    return await svc.create(data)


@router.get("/", response_model=PaginatedResponse[TribeData])
async def list_tribes(limit: int = 20, offset: int = 0, svc: TribeService = Depends(get_service)):
    """List all tribes. Public."""
    items, total = await svc.list(limit, offset)
    return PaginatedResponse(
        message="Tribes retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
    )


@router.get("/{tribe_id}", response_model=TribeResponse)
async def get_tribe(tribe_id: uuid.UUID, svc: TribeService = Depends(get_service)):
    return await svc.get(tribe_id)


@router.patch("/{tribe_id}", response_model=TribeResponse)
async def update_tribe(
    tribe_id: uuid.UUID,
    data: TribeUpdate,
    svc: TribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Update a tribe. Admin only."""
    return await svc.update(tribe_id, data)


@router.delete("/{tribe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tribe(
    tribe_id: uuid.UUID,
    svc: TribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Delete a tribe. Admin only."""
    await svc.delete(tribe_id)
