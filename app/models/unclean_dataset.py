import uuid
import enum

from sqlalchemy import Column, Text, Float, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class DatasetLevelEnum(str, enum.Enum):
    level_1 = "level_1"
    level_2 = "level_2"
    level_3 = "level_3"


class UncleanDataset(TimestampMixin, Base):
    """Raw dataset entry awaiting crowdsourced validation."""

    __tablename__ = "unclean_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    original_text = Column(Text, nullable=False)
    level = Column(SAEnum(DatasetLevelEnum, name="dataset_level_enum"), nullable=False)
    response_percentage = Column(Float, default=0.0, nullable=False)
    is_clean = Column(Boolean, default=False, nullable=False)

    language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=False)

    # Relationships
    allowed_categories = relationship("Category", secondary="dataset_categories", backref="datasets")
    language = relationship("Language", back_populates="unclean_datasets")
    responses = relationship("Response", back_populates="dataset")

    @property
    def ai_responses(self):
        return [r for r in self.responses if r.is_ai_generated]
