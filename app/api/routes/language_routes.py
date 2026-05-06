import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.language import LanguageCreate, LanguageResponse, LanguageUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.language_service import LanguageService

router = APIRouter(prefix="/languages", tags=["Languages"])


def get_service(db: AsyncSession = Depends(get_db)) -> LanguageService:
    return LanguageService(db)


@router.post("/", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
async def create_language(
    data: LanguageCreate,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.create(data)


@router.get("/", response_model=PaginatedResponse[LanguageResponse])
async def list_languages(limit: int = 20, offset: int = 0, svc: LanguageService = Depends(get_service)):
    items, total = await svc.list(limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{language_id}", response_model=LanguageResponse)
async def get_language(language_id: uuid.UUID, svc: LanguageService = Depends(get_service)):
    return await svc.get(language_id)


@router.patch("/{language_id}", response_model=LanguageResponse)
async def update_language(
    language_id: uuid.UUID,
    data: LanguageUpdate,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.update(language_id, data)


@router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(
    language_id: uuid.UUID,
    svc: LanguageService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    await svc.delete(language_id)
