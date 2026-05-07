from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User, RoleEnum


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that allows only users with role='admin'."""
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only.",
        )
    return current_user
