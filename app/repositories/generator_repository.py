from abc import ABC, abstractmethod
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.services.generatorService import AIServiceFactory
from app.models.unclean_dataset import UncleanDataset, DatasetLevelEnum
from app.models.dataset_category import DatasetCategory
from app.models.category import Category


class BaseGeneratorRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_response_from_generatorservice(self, user_input: str, system_prompt: str) -> str:
        pass

    @abstractmethod
    async def update_response_todb(self, generated_text: str, language_id: uuid.UUID, level: DatasetLevelEnum = DatasetLevelEnum.level_1) -> UncleanDataset:
        pass


class GeneratorRepository(BaseGeneratorRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_response_from_generatorservice(self, user_input: str, system_prompt: str) -> str:
        try:
            ai_service = AIServiceFactory.get_service()
            response_text = ai_service.get_response(user_input, system_prompt)
            return response_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate text from AI: {str(e)}")

    async def update_response_todb(self, generated_text: str, language_id: uuid.UUID, level: DatasetLevelEnum = DatasetLevelEnum.level_1) -> UncleanDataset:
        try:
            # 1. Fetch all category IDs
            result = await self.db.execute(select(Category.id))
            all_category_ids = [row[0] for row in result.all()]
            
            if not all_category_ids:
                raise HTTPException(status_code=400, detail="No categories available in the database. Please create categories first.")

            # 2. Create the UncleanDataset
            dataset = UncleanDataset(
                id=uuid.uuid4(),
                original_text=generated_text,
                level=level,
                language_id=language_id
            )
            self.db.add(dataset)
            await self.db.flush()
            
            # 3. Associate all categories
            for cat_id in all_category_ids:
                self.db.add(DatasetCategory(dataset_id=dataset.id, category_id=cat_id))
                
            await self.db.commit()
            await self.db.refresh(dataset)
            return dataset
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save generated dataset: {str(e)}")


