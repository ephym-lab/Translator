import uuid
from abc import ABC, abstractmethod
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.user import User
from app.models.otp import OTP
from app.models.refresh_token import RefreshToken


class BaseUserRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_by_email_or_username(self, email: str, username: str) -> User | None: ...

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> tuple[list[User], int]: ...

    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user: User) -> None: ...

    @abstractmethod
    async def create_otp(self, otp: OTP) -> None: ...

    @abstractmethod
    async def get_unused_otp(self, email: str, code: str) -> OTP | None: ...

    @abstractmethod
    async def save_otp(self, otp: OTP) -> None: ...

    @abstractmethod
    async def create_refresh_token(self, token: RefreshToken) -> None: ...

    @abstractmethod
    async def get_refresh_token(self, token: str) -> RefreshToken | None: ...

    @abstractmethod
    async def delete_refresh_token(self, token: RefreshToken) -> None: ...


class UserRepository(BaseUserRepository):
    """Handles all User, OTP, and RefreshToken DB operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        try:
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.languages))
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch user") from e

    async def get_by_email(self, email: str) -> User | None:
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch user" + str(e)) from e

    async def get_by_email_or_username(self, email: str, username: str) -> User | None:
        try:
            result = await self.db.execute(
                select(User).where(or_(User.email == email, User.username == username))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch user") from e

    async def get_all(self, limit: int, offset: int) -> tuple[list[User], int]:
        try:
            total = (await self.db.execute(select(func.count(User.id)))).scalar()
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.languages))
                .limit(limit)
                .offset(offset)
            )
            return list(result.scalars().all()), total
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to list users") from e

    async def create(self, user: User) -> User:
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to create user") from e

    async def save(self, user: User) -> User:
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to update user") from e

    async def delete(self, user: User) -> None:
        try:
            await self.db.delete(user)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to delete user"+str(e)) from e

    # OTP

    async def create_otp(self, otp: OTP) -> None:
        try:
            self.db.add(otp)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to stage OTP") from e
        # Committed alongside the user in the service (same transaction)

    async def get_unused_otp(self, email: str, code: str) -> OTP | None:
        try:
            result = await self.db.execute(
                select(OTP)
                .where(OTP.email == email, OTP.code == code, OTP.is_used.is_(False))
                .order_by(OTP.created_at.desc())
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch OTP") from e

    async def save_otp(self, otp: OTP) -> None:
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error: failed to save OTP") from e

    # Refresh Token

    async def create_refresh_token(self, token: RefreshToken) -> None:
        try:
            self.db.add(token)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to stage refresh token") from e

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        try:
            result = await self.db.execute(
                select(RefreshToken).where(RefreshToken.token == token)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to fetch refresh token") from e

    async def delete_refresh_token(self, token: RefreshToken) -> None:
        try:
            await self.db.delete(token)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error: failed to delete refresh token") from e

