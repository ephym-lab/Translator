import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_otp,
)
from app.models.otp import OTP
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, LoginRequest, TokenResponse
from app.services.email_service import email_service


class BaseUserService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def register(self, data: UserCreate) -> dict: ...

    @abstractmethod
    async def verify_otp(self, email: str, code: str) -> dict: ...

    @abstractmethod
    async def login(self, data: LoginRequest) -> TokenResponse: ...

    @abstractmethod
    async def refresh(self, token: str) -> TokenResponse: ...

    @abstractmethod
    async def get_user(self, user_id: uuid.UUID) -> User: ...

    @abstractmethod
    async def list_users(self, limit: int, offset: int) -> tuple[list[User], int]: ...

    @abstractmethod
    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User: ...

    @abstractmethod
    async def delete_user(self, user_id: uuid.UUID) -> None: ...


class UserService(BaseUserService):
    """Business logic layer — all DB operations delegated to UserRepository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> dict:
        # Business rule: unique email + username
        existing = await self.repo.get_by_email_or_username(data.email, data.username)
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email or username already registered.")

        user = User(
            id=uuid.uuid4(),
            username=data.username,
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
            gender=data.gender,
            phone=data.phone,
            avatar=data.avatar,
            language_id=data.language_id,
        )

        otp_code = generate_otp()
        otp = OTP(
            id=uuid.uuid4(),
            email=data.email,
            code=otp_code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )

        # Both persisted in one commit via repo
        await self.repo.create_otp(otp)
        await self.repo.create(user)

        await email_service.send_otp_email(data.email, otp_code)
        return {
                    "message": "Registration successful. Check your email for the OTP.",
                    "data":{
                        "user_id":str(user.id),
                        "email":user.email,
                        "username":user.username,
                        "name":user.name,
                        "gender":user.gender,
                        "phone":user.phone,
                        "avatar":user.avatar,
                        
                    }
               }

    async def verify_otp(self, email: str, code: str) -> dict:
        otp = await self.repo.get_unused_otp(email, code)
        if not otp:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or already used OTP.")
        if otp.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "OTP has expired.")

        otp.is_used = True

        # Business rule: mark user as verified
        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        user.is_verified = True

        await self.repo.save_otp(otp)
        await email_service.send_welcome_email(email)
        return {"message": "Email verified successfully."}

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(data.email)

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")

        if not user.is_verified:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Please verify your email first.")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated.")

        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        rt = RefreshToken(
            id=uuid.uuid4(),
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.repo.create_refresh_token(rt)
        await self.db.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, token: str) -> TokenResponse:
        from jose import JWTError
        try:
            payload = decode_token(token)
            if payload.get("type") != "refresh":
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token.")
            user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired or invalid.")

        stored = await self.repo.get_refresh_token(token)
        if not stored:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token not found or revoked.")

        # Token rotation — delete old, issue new
        await self.repo.delete_refresh_token(stored)

        token_data = {"sub": user_id}
        new_access = create_access_token(token_data)
        new_refresh = create_refresh_token(token_data)

        new_rt = RefreshToken(
            id=uuid.uuid4(),
            token=new_refresh,
            user_id=uuid.UUID(user_id),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.repo.create_refresh_token(new_rt)
        await self.db.commit()

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        return user

    async def list_users(self, limit: int = 20, offset: int = 0) -> tuple[list[User], int]:
        return await self.repo.get_all(limit, offset)

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_user(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return await self.repo.save(user)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_user(user_id)
        await self.repo.delete(user)
