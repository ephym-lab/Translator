import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import (
    LoginRequest, OTPVerify, RefreshRequest,
    TokenResponse, UserCreate, UserResponse, UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, svc: UserService = Depends(get_service)):
    """Register a new user. Returns an OTP code (remove from response in production)."""
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
    # _: User = Depends(get_current_user),
):
    await svc.delete_user(user_id)
