import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.tribe import TribeCreate, TribeData, TribeUpdate,TribeResponse
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.services.tribe_service import TribeService

router = APIRouter(prefix="/tribes", tags=["Tribes"])


def get_service(db: AsyncSession = Depends(get_db)) -> TribeService:
    return TribeService(db)


@router.post("/", response_model=APIResponse[TribeResponse], status_code=status.HTTP_201_CREATED)
async def create_tribe(
    data: TribeCreate,
    svc: TribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Create a tribe. Admin only."""
    result = await svc.create(data)
    return APIResponse(success=True, message="Tribe created successfully.", data=result, status=status.HTTP_201_CREATED)


@router.get("/", response_model=APIResponse[PaginatedData[TribeData]])
async def list_tribes(limit: int = 20, offset: int = 0, svc: TribeService = Depends(get_service)):
    """List all tribes. Public."""
    items, total = await svc.list(limit, offset)
    return APIResponse(
        success=True,
        message="Tribes retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )


@router.get("/{tribe_id}", response_model=APIResponse[TribeData])
async def get_tribe(tribe_id: uuid.UUID, svc: TribeService = Depends(get_service)):
    result = await svc.get(tribe_id)
    return APIResponse(success=True, message="Tribe retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.patch("/{tribe_id}", response_model=APIResponse[TribeData])
async def update_tribe(
    tribe_id: uuid.UUID,
    data: TribeUpdate,
    svc: TribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Update a tribe. Admin only."""
    result = await svc.update(tribe_id, data)
    return APIResponse(success=True, message="Tribe updated successfully.", data=result, status=status.HTTP_200_OK)


@router.delete("/{tribe_id}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def delete_tribe(
    tribe_id: uuid.UUID,
    svc: TribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Delete a tribe. Admin only."""
    await svc.delete(tribe_id)
    return APIResponse(success=True, message="Tribe deleted successfully.", status=status.HTTP_200_OK)
