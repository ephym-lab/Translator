from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list wrapper for all list endpoints."""

    total: int
    limit: int
    offset: int
    items: Sequence[T]

    model_config = {"from_attributes": True}
