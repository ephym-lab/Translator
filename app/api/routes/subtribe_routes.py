import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.subtribe import SubTribeCreate, SubTribeData, SubTribeUpdate
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.services.subtribe_service import SubTribeService

router = APIRouter(prefix="/subtribes", tags=["SubTribes"])


def get_service(db: AsyncSession = Depends(get_db)) -> SubTribeService:
    return SubTribeService(db)


@router.post("/", response_model=APIResponse[SubTribeData], status_code=status.HTTP_201_CREATED)
async def create_subtribe(
    data: SubTribeCreate,
    svc: SubTribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Create a subtribe. Admin only."""
    result = await svc.create(data)
    return APIResponse(success=True, message="SubTribe created successfully.", data=result, status=status.HTTP_201_CREATED)


@router.get("/", response_model=APIResponse[PaginatedData[SubTribeData]])
async def list_subtribes(
    limit: int = 20,
    offset: int = 0,
    tribe_id: Optional[uuid.UUID] = None,
    svc: SubTribeService = Depends(get_service),
):
    """List subtribes. Optional filter by tribe_id. Public."""
    items, total = await svc.list_all(limit, offset, tribe_id=tribe_id)
    return APIResponse(
        success=True,
        message="SubTribes retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK,
    )


@router.get("/by-tribe/{tribe_id}", response_model=APIResponse[list[SubTribeData]])
async def get_subtribes_by_tribe_id(
    tribe_id: uuid.UUID,
    svc: SubTribeService = Depends(get_service),
):
    """Get all subtribes belonging to a tribe. Public."""
    result = await svc.get_by_tribe_id(tribe_id)
    return APIResponse(success=True, message="SubTribes retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.get("/{subtribe_id}", response_model=APIResponse[SubTribeData])
async def get_subtribe(subtribe_id: uuid.UUID, svc: SubTribeService = Depends(get_service)):
    result = await svc.get(subtribe_id)
    return APIResponse(success=True, message="SubTribe retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.patch("/{subtribe_id}", response_model=APIResponse[SubTribeData])
async def update_subtribe(
    subtribe_id: uuid.UUID,
    data: SubTribeUpdate,
    svc: SubTribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Update a subtribe. Admin only."""
    result = await svc.update(subtribe_id, data)
    return APIResponse(success=True, message="SubTribe updated successfully.", data=result, status=status.HTTP_200_OK)


@router.delete("/{subtribe_id}", response_model=APIResponse[None], response_model_exclude_none=True)
async def delete_subtribe(
    subtribe_id: uuid.UUID,
    svc: SubTribeService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Delete a subtribe. Admin only."""
    await svc.delete(subtribe_id)
    return APIResponse(success=True, message="SubTribe deleted successfully.", status=status.HTTP_200_OK)