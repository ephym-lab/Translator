import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.dataset import DatasetCreate, DatasetResponse, DatasetUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])


def get_service(db: AsyncSession = Depends(get_db)) -> DatasetService:
    return DatasetService(db)


@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    data: DatasetCreate,
    svc: DatasetService = Depends(get_service),
    _: User = Depends(require_admin),
):
    return await svc.create(data)


@router.get("/", response_model=PaginatedResponse[DatasetResponse])
async def list_datasets(limit: int = 20, offset: int = 0, svc: DatasetService = Depends(get_service)):
    items, total = await svc.list(limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: uuid.UUID, svc: DatasetService = Depends(get_service)):
    return await svc.get(dataset_id)


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: uuid.UUID,
    data: DatasetUpdate,
    svc: DatasetService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.update(dataset_id, data)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: uuid.UUID,
    svc: DatasetService = Depends(get_service),
    _: User = Depends(require_admin),
):
    await svc.delete(dataset_id)
