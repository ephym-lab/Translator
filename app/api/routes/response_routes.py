import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.dataset import DatasetResponse
from app.schemas.response import ResponseCreate, ResponseSchema, ResponseUpdate
from app.schemas.pagination import PaginatedResponse, PaginatedData
from app.services.response_service import ResponseService

router = APIRouter(prefix="/responses", tags=["Responses"])


def get_service(db: AsyncSession = Depends(get_db)) -> ResponseService:
    return ResponseService(db)


@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def submit_response(
    data: ResponseCreate,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    """Submit a response to a dataset entry in a specific language.
    Returns 409 if you already responded in that language for this dataset."""
    return await svc.submit(current_user.id, data)


@router.get("/next", response_model=DatasetResponse)
async def get_next_dataset(
    language_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    """Get the next unseen dataset for the current user in the given language.
    language_id must be one of the user's registered languages.
    Records a session so the same dataset is not served twice."""
    return await svc.next_dataset(current_user.id, language_id)


@router.get("/", response_model=PaginatedResponse[ResponseSchema])
async def list_all_responses(
    limit: int = 20,
    offset: int = 0,
    language_id: Optional[uuid.UUID] = None,
    svc: ResponseService = Depends(get_service),
):
    """List all responses. Optionally filter by language_id."""
    items, total = await svc.list_all(limit, offset, language_id=language_id)
    return PaginatedResponse(
        message="Responses retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
    )


@router.get("/dataset/{dataset_id}", response_model=PaginatedResponse[ResponseSchema])
async def list_responses_for_dataset(
    dataset_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    language_id: Optional[uuid.UUID] = None,
    svc: ResponseService = Depends(get_service),
):
    """List responses for a specific dataset. Optionally filter by language_id
    to see e.g. all Kikuyu translations of a specific text."""
    items, total = await svc.list_by_dataset(dataset_id, limit, offset, language_id=language_id)
    return PaginatedResponse(
        message="Responses for dataset retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
    )


@router.get("/{response_id}", response_model=ResponseSchema)
async def get_response(response_id: uuid.UUID, svc: ResponseService = Depends(get_service)):
    return await svc.get(response_id)


@router.patch("/{response_id}", response_model=ResponseSchema)
async def update_response(
    response_id: uuid.UUID,
    data: ResponseUpdate,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    return await svc.update(response_id, current_user.id, data)


@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_response(
    response_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    await svc.delete(response_id, current_user.id)
