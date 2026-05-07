from typing import Generic, Sequence, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedData(BaseModel,Generic[T]):
    total: int
    limit: int
    offset: int
    items: Sequence[T]

    model_config = {"from_attributes": True}

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list wrapper for all list endpoints."""
    message: str
    data: PaginatedData[T]
