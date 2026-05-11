from abc import ABC, abstractmethod
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.services.generatorService import AIServiceFactory
from app.models.unclean_dataset import UncleanDataset, DatasetLevelEnum
from app.models.dataset_category import DatasetCategory
from app.models.category import Category
from app.repositories.dataset_repository import DatasetRepository
from app.services.ai_translation_service import generate_ai_responses_for_dataset


class BaseGeneratorRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_response_from_generatorservice(
        self,
        system_prompt: str,
        language_id: uuid.UUID,
        level: DatasetLevelEnum,
        user_input: str | None = None,
    ) -> str:
        pass

    @abstractmethod
    async def update_response_todb(
        self,
        generated_text: str,
        language_id: uuid.UUID,
        category_ids: list[uuid.UUID],
        level: DatasetLevelEnum = DatasetLevelEnum.level_1,
    ) -> UncleanDataset:
        pass

    @abstractmethod
    async def get_dataset_with_categories(
        self, dataset_id: uuid.UUID
    ) -> UncleanDataset | None:
        pass


class GeneratorRepository(BaseGeneratorRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_response_from_generatorservice(
        self,
        system_prompt: str,
        language_id: uuid.UUID,
        level: DatasetLevelEnum,
        user_input: str | None = None,
    ) -> str:
        # Use caller-supplied prompt or auto-generate one
        if not user_input:
            user_input = (
                f"Generate a sample text for a translation dataset. "
                f"Language ID: {language_id}. "
                f"Difficulty level: {level.value}. "
                f"Return plain text only, no explanations."
            )
        try:
            ai_service = AIServiceFactory.get_service()
            response_text = await asyncio.get_event_loop().run_in_executor(
                None, ai_service.get_response, user_input, system_prompt
            )
            return response_text
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate text from AI: {str(e)}",
            )

    async def update_response_todb(
        self,
        generated_text: str,
        language_id: uuid.UUID,
        category_ids: list[uuid.UUID],
        level: DatasetLevelEnum = DatasetLevelEnum.level_1,
    ) -> UncleanDataset:
        try:
            if not category_ids:
                # Fetch all available category IDs and assign them all
                result = await self.db.execute(select(Category.id))
                all_category_ids = [row[0] for row in result.all()]

                if not all_category_ids:
                    raise HTTPException(
                        status_code=400,
                        detail="No categories available in the database. Please create categories first.",
                    )

                dataset = UncleanDataset(
                    id=uuid.uuid4(),
                    original_text=generated_text,
                    level=level,
                    language_id=language_id,
                )
                self.db.add(dataset)
                await self.db.flush()

                for cat_id in all_category_ids:
                    self.db.add(DatasetCategory(dataset_id=dataset.id, category_id=cat_id))

                await self.db.commit()
                await self.db.refresh(dataset)
                
                # Dispatch background task for translation
                asyncio.create_task(
                    generate_ai_responses_for_dataset(
                        dataset_id=dataset.id,
                        original_text=dataset.original_text,
                        category_ids=all_category_ids
                    )
                )
                
                return dataset

            else:
                dataset_repo = DatasetRepository(self.db)
                dataset = await dataset_repo.create(
                    data={
                        "original_text": generated_text,
                        "language_id": language_id,
                        "level": level,
                    },
                    category_ids=category_ids,
                )
                
                # Dispatch background task for translation
                asyncio.create_task(
                    generate_ai_responses_for_dataset(
                        dataset_id=dataset.id,
                        original_text=dataset.original_text,
                        category_ids=category_ids
                    )
                )
                
                return dataset

        except HTTPException:
            # Let already-typed HTTP errors propagate without wrapping them
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save generated dataset: {str(e)}",
            )

    async def get_dataset_with_categories(
        self, dataset_id: uuid.UUID
    ) -> UncleanDataset | None:
        # Encapsulates the eager-load query so the router stays clean
        result = await self.db.execute(
            select(UncleanDataset)
            .options(selectinload(UncleanDataset.allowed_categories))
            .where(UncleanDataset.id == dataset_id)
        )
        return result.scalar_one_or_none()