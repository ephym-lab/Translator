import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.language import LanguageNestedResponse
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import (
    AddLanguageRequest, LoginRequest, OTPVerify, RefreshRequest,
    TokenResponse, UserCreate, UserResponse, UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, svc: UserService = Depends(get_service)):
    """Register a new user. Accepts a list of language_ids."""
    return await svc.register(data)


@router.post("/verify-otp")
async def verify_otp(data: OTPVerify, svc: UserService = Depends(get_service)):
    """Verify the email OTP to activate the account."""
    return await svc.verify_otp(data.email, data.code)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, svc: UserService = Depends(get_service)):
    """Authenticate and receive an access + refresh token pair."""
    return await svc.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, svc: UserService = Depends(get_service)):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    return await svc.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Update the currently authenticated user's profile."""
    return await svc.update_user(current_user.id, data)


# ─── User language management ─────────────────────────────────────────────────

@router.get("/me/languages", response_model=list[LanguageNestedResponse])
async def get_my_languages(
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Return all languages linked to the current user (with full nested subtribe/tribe)."""
    return await svc.get_user_languages(current_user.id)


@router.post("/me/languages", response_model=list[LanguageNestedResponse], status_code=status.HTTP_201_CREATED)
async def add_my_language(
    data: AddLanguageRequest,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Add a language to the current user's profile. No duplicates allowed."""
    return await svc.add_language(current_user.id, data.language_id)


@router.delete("/me/languages/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_my_language(
    language_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_service),
):
    """Remove a language from the current user's profile."""
    await svc.remove_language(current_user.id, language_id)


#Admin endpoints 

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    limit: int = 20,
    offset: int = 0,
    svc: UserService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    """List all users (paginated). Requires authentication."""
    users, total = await svc.list_users(limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=users)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    svc: UserService = Depends(get_service),
    _: User = Depends(get_current_user),
):
    return await svc.get_user(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    svc: UserService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Delete a user. Admin only."""
    await svc.delete_user(user_id)

#delete user by email
@router.delete("/delete/{email}")
async def delete_user_by_email(
    email: str,
    svc: UserService = Depends(get_service)
):
    return await svc.delete_user_by_email(email)