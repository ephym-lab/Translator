from pydantic import BaseModel
import uuid
from typing import List, Optional
from app.models.unclean_dataset import DatasetLevelEnum

class GenerateDatasetRequest(BaseModel):
    # If omitted, the repo auto-builds a prompt from language_id + level
    user_input: Optional[str] = None
    system_prompt: Optional[str] = "You are a helpful AI that generates sample texts for translation datasets."
    language_id: uuid.UUID
    # Empty list (default) → all available categories are assigned
    category_ids: List[uuid.UUID] = []
    level: DatasetLevelEnum = DatasetLevelEnum.level_1
