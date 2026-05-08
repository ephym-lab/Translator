import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.language import LanguageNestedResponse
from app.schemas.pagination import PaginatedData
from app.schemas.api_response import APIResponse
from app.schemas.user import (
    AddLanguageRequest, LoginRequest, OTPVerify, RefreshRequest,
    TokenResponse, UserCreate, UserResponse, UserUpdate, LoginResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/register", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, svc: UserService = Depends(get_service)):
    """Register a new user. Accepts a list of language_ids."""
    result = await svc.register(data)
    return APIResponse(success=True, message="User registered successfully.", data=result, status=status.HTTP_201_CREATED)


@router.post("/verify-otp", response_model=APIResponse[dict])
async def verify_otp(data: OTPVerify, svc: UserService = Depends(get_service)):
    """Verify the email OTP to activate the account."""
    result = await svc.verify_otp(data.email, data.code)
    return APIResponse(success=True, message="OTP verified successfully.", data=result, status=status.HTTP_200_OK)


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(data: LoginRequest, svc: UserService = Depends(get_service)):
    """Authenticate and receive an access + refresh token pair."""
    result = await svc.login(data)
    return APIResponse(success=True, message="Logged in successfully.", data=result, status=status.HTTP_200_OK)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(data: RefreshRequest, svc: UserService = Depends(get_service)):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    result = await svc.refresh(data.refresh_token)
    return APIResponse(success=True, message="Token refreshed successfully.", data=result, status=status.HTTP_200_OK)


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return APIResponse(success=True, message="Profile retrieved successfully.", data=current_user, status=status.HTTP_200_OK)


@router.patch("/me", response_model=APIResponse[UserResponse])
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Update the currently authenticated user's profile."""
    result = await svc.update_user(current_user.id, data)
    return APIResponse(success=True, message="Profile updated successfully.", data=result, status=status.HTTP_200_OK)


# ─── User language management ─────────────────────────────────────────────────

@router.get("/me/languages", response_model=APIResponse[list[LanguageNestedResponse]])
async def get_my_languages(
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Return all languages linked to the current user (with full nested subtribe/tribe)."""
    result = await svc.get_user_languages(current_user.id)
    return APIResponse(success=True, message="Languages retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.post("/me/languages", response_model=APIResponse[list[LanguageNestedResponse]], status_code=status.HTTP_201_CREATED)
async def add_my_language(
    data: AddLanguageRequest,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Add a language to the current user's profile. No duplicates allowed."""
    result = await svc.add_language(current_user.id, data.language_id)
    return APIResponse(success=True, message="Language added successfully.", data=result, status=status.HTTP_201_CREATED)


@router.delete("/me/languages/{language_id}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def remove_my_language(
    language_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Remove a language from the current user's profile."""
    await svc.remove_language(current_user.id, language_id)
    return APIResponse(success=True, message="Language removed successfully.", status=status.HTTP_200_OK)


# ─── Admin endpoints ──────────────────────────────────────────────────────────

@router.get("/", response_model=APIResponse[PaginatedData[UserResponse]])
async def list_users(
    limit: int = 20,
    offset: int = 0,
    svc: UserService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    """List all users (paginated). Requires authentication."""
    users, total = await svc.list_users(limit, offset)
    return APIResponse(
        success=True,
        message="Users retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=users),
        status=status.HTTP_200_OK
    )


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: uuid.UUID,
    svc: UserService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    result = await svc.get_user(user_id)
    return APIResponse(success=True, message="User retrieved successfully.", data=result, status=status.HTTP_200_OK)


@router.delete("/{user_id}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: uuid.UUID,
    svc: UserService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Delete a user. Admin only."""
    await svc.delete_user(user_id)
    return APIResponse(success=True, message="User deleted successfully.", status=status.HTTP_200_OK)


@router.delete("/delete/{email}", response_model=APIResponse[None], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def delete_user_by_email(
    email: str,
    svc: UserService = Depends(get_service),
):
    await svc.delete_user_by_email(email)
    return APIResponse(success=True, message="User deleted successfully.", status=status.HTTP_200_OK)