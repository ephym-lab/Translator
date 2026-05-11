import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.dataset import DatasetCreate, DatasetResponse, DatasetUpdate
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])


def get_service(db: AsyncSession = Depends(get_db)) -> DatasetService:
    return DatasetService(db)


@router.post("/", response_model=APIResponse[DatasetResponse], status_code=status.HTTP_201_CREATED)
async def create_dataset(
    data: DatasetCreate,
    svc: DatasetService = Depends(get_service),
    _: User = Depends(require_admin),
):
    result = await svc.create(data)
    return APIResponse(success=True, message="Dataset created successfully.", data=result, status=status.HTTP_201_CREATED)


@router.get("/", response_model=APIResponse[PaginatedData[DatasetResponse]])
async def list_datasets(limit: int = 20, offset: int = 0, svc: DatasetService = Depends(get_service)):
    items, total = await svc.list(limit, offset)
    return APIResponse(
        success=True,
        message="Datasets retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )


@router.get("/ai-generated", response_model=APIResponse[PaginatedData[DatasetResponse]])
async def list_ai_generated_datasets(limit: int = 20, offset: int = 0, svc: DatasetService = Depends(get_service)):
    """Get datasets that contain AI-generated responses (for users to vote on or reply to)."""
    items, total = await svc.list_with_ai_responses(limit, offset)
    return APIResponse(
        success=True,
        message="AI-generated datasets retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )


@router.get("/{dataset_id}", response_model=APIResponse[DatasetResponse])
async def get_dataset(dataset_id: uuid.UUID, svc: DatasetService = Depends(get_service)):
    result = await svc.get(dataset_id)
    return APIResponse(success=True, message="Dataset retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.get("/{dataset_id}/responses/count", response_model=APIResponse[dict])
async def get_responses_count(dataset_id: uuid.UUID, svc: DatasetService = Depends(get_service)):
    """Get the total and accepted responses count for a specific dataset."""
    result = await svc.get_responses_count(dataset_id)
    return APIResponse(success=True, message="Responses count retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.patch("/{dataset_id}", response_model=APIResponse[DatasetResponse])
async def update_dataset(
    dataset_id: uuid.UUID,
    data: DatasetUpdate,
    svc: DatasetService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    result = await svc.update(dataset_id, data)
    return APIResponse(success=True, message="Dataset updated successfully.", data=result, status=status.HTTP_200_OK)


@router.delete("/{dataset_id}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def delete_dataset(
    dataset_id: uuid.UUID,
    svc: DatasetService = Depends(get_service),
    _: User = Depends(require_admin),
):
    await svc.delete(dataset_id)
    return APIResponse(success=True, message="Dataset deleted successfully.", status=status.HTTP_200_OK)
