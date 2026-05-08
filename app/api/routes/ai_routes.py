import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.repositories.generator_repository import GeneratorRepository
from app.schemas.ai import GenerateDatasetRequest
from app.schemas.dataset import DatasetResponse
from app.schemas.api_response import APIResponse

router = APIRouter(prefix="/ai", tags=["AI Generation"])

def get_generator_repo(db: AsyncSession = Depends(get_db)) -> GeneratorRepository:
    return GeneratorRepository(db)


@router.post("/generate-dataset", response_model=APIResponse[DatasetResponse], status_code=status.HTTP_201_CREATED)
async def generate_dataset(
    data: GenerateDatasetRequest,
    repo: GeneratorRepository = Depends(get_generator_repo),
    _: User = Depends(require_admin),
):
    """
    Generate a new dataset entry using the AI service and save it to the database.
    Automatically assigns all available categories to the generated dataset.
    Admin only.
    """
    # 1. Generate text from AI
    generated_text = await repo.get_response_from_generatorservice(
        user_input=data.user_input,
        system_prompt=data.system_prompt
    )
    
    # Check if there was an error string returned by the service
    if generated_text.startswith('{"content": "Error calling'):
        raise HTTPException(status_code=502, detail=generated_text)

    # 2. Save to database with all categories
    dataset = await repo.update_response_todb(
        generated_text=generated_text,
        language_id=data.language_id,
        level=data.level
    )
    
    # 3. We need to load the allowed_categories to satisfy the DatasetResponse schema.
    # The repository already committed and refreshed, but we need eager-loaded categories.
    # Let's do a quick query to fetch the full object.
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.unclean_dataset import UncleanDataset
    
    result = await repo.db.execute(
        select(UncleanDataset)
        .options(selectinload(UncleanDataset.allowed_categories))
        .where(UncleanDataset.id == dataset.id)
    )
    full_dataset = result.scalar_one_or_none()
    
    return APIResponse(success=True, message="Dataset generated successfully.", data=full_dataset, status=status.HTTP_201_CREATED)
