import asyncio
import uuid
import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.language import Language
from app.models.response import Response
from app.services.TTTService import NLLBTTTService

logger = logging.getLogger(__name__)

async def generate_ai_responses_for_dataset(dataset_id: uuid.UUID, original_text: str, category_ids: list[uuid.UUID]):
    """
    Background task to generate AI translations for a dataset across all languages.
    """
    ttt_service = NLLBTTTService()
    
    async with AsyncSessionLocal() as db:
        try:
            # Get all languages
            result = await db.execute(select(Language))
            languages = result.scalars().all()
            
            responses_to_insert = []
            
            for lang in languages:
                if lang.name.lower() == "english":
                    continue
                
                try:
                    translated_text = await ttt_service.translate_async(
                        text=original_text,
                        source_lang="english",
                        target_lang=lang.name
                    )
                    
                    if not translated_text:
                        continue
                        
                    for cat_id in category_ids:
                        response = Response(
                            id=uuid.uuid4(),
                            response_text=translated_text,
                            dataset_id=dataset_id,
                            language_id=lang.id,
                            category_id=cat_id,
                            is_ai_generated=True,
                            user_id=None
                        )
                        responses_to_insert.append(response)
                        
                except Exception as e:
                    logger.error(f"Failed to translate dataset {dataset_id} to {lang.name}: {e}")
            
            if responses_to_insert:
                db.add_all(responses_to_insert)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error in generate_ai_responses_for_dataset: {e}")
