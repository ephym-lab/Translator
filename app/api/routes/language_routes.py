import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.language import LanguageCreate, LanguageData, LanguageUpdate, LanguageResponse
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.services.language_service import LanguageService

router = APIRouter(prefix="/languages", tags=["Languages"])


def get_service(db: AsyncSession = Depends(get_db)) -> LanguageService:
    return LanguageService(db)


@router.post("/", response_model=APIResponse[LanguageResponse], status_code=status.HTTP_201_CREATED)
async def create_language(
    data: LanguageCreate,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Create a language. Admin only."""
    result = await svc.create(data)
    return APIResponse(success=True, message="Language created successfully.", data=result, status=status.HTTP_201_CREATED)


@router.get("/", response_model=APIResponse[PaginatedData[LanguageData]])
async def list_languages(
    limit: int = 20,
    offset: int = 0,
    subtribe_id: Optional[uuid.UUID] = None,
    svc: LanguageService = Depends(get_service),
):
    """List languages. Optional filter by subtribe_id (for cascading dropdowns). Public."""
    items, total = await svc.listall(limit, offset, subtribe_id=subtribe_id)
    return APIResponse(
        success=True,
        message="Languages retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )


@router.get("/{language_id}", response_model=APIResponse[LanguageData])
async def get_language(language_id: uuid.UUID, svc: LanguageService = Depends(get_service)):
    lang = await svc.get(language_id)
    return APIResponse(success=True, message="Language fetched successfully.", data=lang, status=status.HTTP_200_OK)


@router.patch("/{language_id}", response_model=APIResponse[LanguageData])
async def update_language(
    language_id: uuid.UUID,
    data: LanguageUpdate,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Update a language. Admin only."""
    lang = await svc.update(language_id, data)
    return APIResponse(success=True, message="Language updated successfully.", data=lang, status=status.HTTP_200_OK)


@router.delete("/{language_id}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def delete_language(
    language_id: uuid.UUID,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Delete a language. Admin only."""
    await svc.delete(language_id)
    return APIResponse(success=True, message="Language deleted successfully.", status=status.HTTP_200_OK)



