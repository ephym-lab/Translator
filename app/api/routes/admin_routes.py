from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.api_response import APIResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)


@router.get(
    "/stats",
    response_model=APIResponse[dict],
    summary="Platform statistics",
    description=(
        "Returns an aggregated snapshot of the platform: total users, datasets, "
        "tribes, subtribes, languages, categories, responses, acceptance rate, "
        "and voting activity. **Admin only.**"
    ),
)
async def get_platform_stats(
    svc: AdminService = Depends(get_service),
    _: User = Depends(require_admin),
):
    """Aggregate platform-wide statistics. Requires admin role."""
    data = await svc.get_stats()
    return APIResponse(
        success=True,
        message="Platform statistics retrieved successfully.",
        data=data,
        status=status.HTTP_200_OK,
    )
