import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    svc: CategoryService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.create(data)


@router.get("/", response_model=PaginatedResponse[CategoryResponse])
async def list_categories(limit: int = 20, offset: int = 0, svc: CategoryService = Depends(get_service)):
    items, total = await svc.list(limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: uuid.UUID, svc: CategoryService = Depends(get_service)):
    return await svc.get(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    svc: CategoryService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    svc: CategoryService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    await svc.delete(category_id)
