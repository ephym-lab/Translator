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
from app.repositories.language_repository import LanguageRepository

router = APIRouter(prefix="/ai", tags=["AI Generation"])


def get_generator_repo(db: AsyncSession = Depends(get_db)) -> GeneratorRepository:
    return GeneratorRepository(db)


def get_language_repo(db: AsyncSession = Depends(get_db)) -> LanguageRepository:
    return LanguageRepository(db)


@router.post(
    "/generate-dataset",
    response_model=APIResponse[DatasetResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_dataset(
    data: GenerateDatasetRequest,
    repo: GeneratorRepository = Depends(get_generator_repo),
    lang_repo: LanguageRepository = Depends(get_language_repo),
    _: User = Depends(require_admin),
):
    """
    Generate a new dataset entry using the AI service and save it to the database.
    Automatically assigns all available categories when none are specified.
    Admin only.
    """
    # 1. Fetch the language to pass its name to the AI
    language = await lang_repo.get_by_id(data.language_id)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language not found.",
        )

    # 2. Generate text from AI — raises HTTPException on failure
    generated_text = await repo.get_response_from_generatorservice(
        system_prompt=data.system_prompt,
        language_name=language.name,
        level=data.level,
        user_input=data.user_input,  
    )

    # 2. Save to database with the given (or all) categories
    dataset = await repo.update_response_todb(
        generated_text=generated_text,
        language_id=data.language_id,
        category_ids=data.category_ids,
        level=data.level,
    )

    # 3. Reload with eager-loaded relationships via the repository method
    full_dataset = await repo.get_dataset_with_categories(dataset.id)

    if full_dataset is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dataset was saved but could not be retrieved.",
        )

    return APIResponse(
        success=True,
        message="Dataset generated successfully.",
        data=full_dataset,
        status=status.HTTP_201_CREATED,
    )