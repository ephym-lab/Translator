import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


@router.post("/", response_model=APIResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    svc: CategoryService = Depends(get_service),
    _: User = Depends(require_admin),
):
    result = await svc.create(data)
    return APIResponse(success=True, message="Category created successfully.", data=result, status=status.HTTP_201_CREATED)


@router.get("/", response_model=APIResponse[PaginatedData[CategoryResponse]])
async def list_categories(limit: int = 20, offset: int = 0, svc: CategoryService = Depends(get_service)):
    items, total = await svc.list(limit, offset)
    return APIResponse(
        success=True,
        message="Categories retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )


@router.get("/{category_id}", response_model=APIResponse[CategoryResponse])
async def get_category(category_id: uuid.UUID, svc: CategoryService = Depends(get_service)):
    result = await svc.get(category_id)
    return APIResponse(success=True, message="Category retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.patch("/{category_id}", response_model=APIResponse[CategoryResponse])
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    svc: CategoryService = Depends(get_service),
    _: User = Depends(require_admin),
):
    result = await svc.update(category_id, data)
    return APIResponse(success=True, message="Category updated successfully.", data=result, status=status.HTTP_200_OK)


@router.delete("/{category_id}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: uuid.UUID,
    svc: CategoryService = Depends(get_service),
    _: User = Depends(require_admin),
):
    await svc.delete(category_id)
    return APIResponse(success=True, message="Category deleted successfully.", status=status.HTTP_200_OK)
