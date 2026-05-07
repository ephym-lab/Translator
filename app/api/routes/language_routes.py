import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.language import LanguageCreate, LanguageResponse, LanguageUpdate,LanguageData
from app.schemas.pagination import PaginatedResponse
from app.services.language_service import LanguageService

router = APIRouter(prefix="/languages", tags=["Languages"])


def get_service(db: AsyncSession = Depends(get_db)) -> LanguageService:
    return LanguageService(db)


@router.post("/", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
async def create_language(
    data: LanguageCreate,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Create a language. Admin only."""
    return await svc.create(data)


@router.get("/", response_model=PaginatedResponse[LanguageData])
async def list_languages(
    limit: int = 20,
    offset: int = 0,
    subtribe_id: Optional[uuid.UUID] = None,
    svc: LanguageService = Depends(get_service),
):
    """List languages. Optional filter by subtribe_id (for cascading dropdowns). Public."""
    items, total = await svc.listall(limit, offset, subtribe_id=subtribe_id)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{language_id}", response_model=LanguageResponse)
async def get_language(language_id: uuid.UUID, svc: LanguageService = Depends(get_service)):
    return await svc.get(language_id)


@router.patch("/{language_id}", response_model=LanguageResponse)
async def update_language(
    language_id: uuid.UUID,
    data: LanguageUpdate,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Update a language. Admin only."""
    return await svc.update(language_id, data)


@router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(
    language_id: uuid.UUID,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Delete a language. Admin only."""
    await svc.delete(language_id)
