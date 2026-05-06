import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.response import ResponseCreate, ResponseSchema, ResponseUpdate
from app.schemas.pagination import PaginatedResponse
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
    """Submit a response to a dataset entry."""
    return await svc.submit(current_user.id, data)


@router.get("/dataset/{dataset_id}", response_model=PaginatedResponse[ResponseSchema])
async def list_responses_for_dataset(
    dataset_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    svc: ResponseService = Depends(get_service),
):
    items, total = await svc.list_by_dataset(dataset_id, limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


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
