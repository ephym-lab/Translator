import uuid
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin

class DatasetCategory(TimestampMixin, Base):
    """Junction table mapping datasets to allowed categories."""
    
    __tablename__ = "dataset_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("unclean_datasets.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("dataset_id", "category_id", name="uq_dataset_category"),
    )
