from pydantic import BaseModel
import uuid
from typing import Optional
from app.models.unclean_dataset import DatasetLevelEnum

class GenerateDatasetRequest(BaseModel):
    user_input: str
    system_prompt: Optional[str] = "You are a helpful AI that generates sample texts for translation datasets."
    language_id: uuid.UUID
    level: DatasetLevelEnum = DatasetLevelEnum.level_1
