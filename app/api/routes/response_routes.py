import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.dataset import DatasetResponse
from app.schemas.response import ResponseCreate, ResponseSchema, ResponseUpdate
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.services.response_service import ResponseService
from app.models.response_vote import VoteEnum

router = APIRouter(prefix="/responses", tags=["Responses"])


def get_service(db: AsyncSession = Depends(get_db)) -> ResponseService:
    return ResponseService(db)


@router.post("/", response_model=APIResponse[ResponseSchema], status_code=status.HTTP_201_CREATED)
async def submit_response(
    data: ResponseCreate,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    """Submit a response to a dataset entry in a specific language.
    Returns 409 if you already responded in that language for this dataset."""
    result = await svc.submit(current_user.id, data)
    return APIResponse(success=True, message="Response submitted successfully.", data=result, status=status.HTTP_201_CREATED)


@router.get("/next", response_model=APIResponse[DatasetResponse])
async def get_next_dataset(
    language_id: uuid.UUID,
    category_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    """Get the next unseen dataset for the current user in the given language.
    language_id must be one of the user's registered languages.
    Records a session so the same dataset is not served twice."""
    result = await svc.next_dataset(current_user.id, language_id, category_id=category_id)
    return APIResponse(success=True, message="Next dataset retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.get("/", response_model=APIResponse[PaginatedData[ResponseSchema]])
async def list_all_responses(
    limit: int = 20,
    offset: int = 0,
    language_id: Optional[uuid.UUID] = None,
    is_ai_generated: Optional[bool] = None,
    vote_type: Optional[VoteEnum] = None,
    svc: ResponseService = Depends(get_service),
):
    """List all responses. Optionally filter by language_id, is_ai_generated, and vote_type."""
    items, total = await svc.list_all(limit, offset, language_id=language_id, is_ai_generated=is_ai_generated, vote_type=vote_type)
    return APIResponse(
        success=True,
        message="Responses retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )


@router.get("/dataset/{dataset_id}", response_model=APIResponse[PaginatedData[ResponseSchema]])
async def list_responses_for_dataset(
    dataset_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    language_id: Optional[uuid.UUID] = None,
    is_ai_generated: Optional[bool] = None,
    vote_type: Optional[VoteEnum] = None,
    svc: ResponseService = Depends(get_service),
):
    """List responses for a specific dataset. Optionally filter by language_id
    to see e.g. all Kikuyu translations of a specific text. You can also filter by vote_type."""
    items, total = await svc.list_by_dataset(dataset_id, limit, offset, language_id=language_id, is_ai_generated=is_ai_generated, vote_type=vote_type)
    return APIResponse(
        success=True,
        message="Responses for dataset retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )


@router.get("/{response_id}", response_model=APIResponse[ResponseSchema])
async def get_response(response_id: uuid.UUID, svc: ResponseService = Depends(get_service)):
    result = await svc.get(response_id)
    return APIResponse(success=True, message="Response retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.patch("/{response_id}", response_model=APIResponse[ResponseSchema])
async def update_response(
    response_id: uuid.UUID,
    data: ResponseUpdate,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    result = await svc.update(response_id, current_user.id, data)
    return APIResponse(success=True, message="Response updated successfully.", data=result, status=status.HTTP_200_OK)


@router.delete("/{response_id}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def delete_response(
    response_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    await svc.delete(response_id, current_user.id)
    return APIResponse(success=True, message="Response deleted successfully.", status=status.HTTP_200_OK)

@router.get("/user/me", response_model=APIResponse[PaginatedData[ResponseSchema]])
async def list_my_responses(
    limit: int = 20,
    offset: int = 0,
    language_id: Optional[uuid.UUID] = None,
    is_ai_generated: Optional[bool] = None,
    vote_type: Optional[VoteEnum] = None,
    current_user: User = Depends(get_current_user),
    svc: ResponseService = Depends(get_service),
):
    """List responses for the current user. Optionally filter by language_id
    to see e.g. all Kikuyu translations of a specific text. You can also filter by vote_type."""
    items, total = await svc.list_by_user(current_user.id, limit, offset, language_id=language_id, is_ai_generated=is_ai_generated, vote_type=vote_type)
    return APIResponse(
        success=True,
        message="Responses for user retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )

#get user responses
@router.get("/user/{user_id}", response_model=APIResponse[PaginatedData[ResponseSchema]])
async def list_user_responses(
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    language_id: Optional[uuid.UUID] = None,
    is_ai_generated: Optional[bool] = None,
    vote_type: Optional[VoteEnum] = None,
    svc: ResponseService = Depends(get_service),
):
    """List responses for a specific user. Optionally filter by language_id
    to see e.g. all Kikuyu translations of a specific text. You can also filter by vote_type."""
    items, total = await svc.list_by_user(user_id, limit, offset, language_id=language_id, is_ai_generated=is_ai_generated, vote_type=vote_type)
    return APIResponse(
        success=True,
        message="Responses for user retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=items),
        status=status.HTTP_200_OK
    )

