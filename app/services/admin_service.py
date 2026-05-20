from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.admin_repository import AdminRepository


class AdminService:
    """Business logic for admin statistics."""

    def __init__(self, db: AsyncSession):
        self.repo = AdminRepository(db)

    async def get_stats(self) -> dict:
        """Return a comprehensive platform statistics snapshot."""
        return await self.repo.get_platform_stats()
