from fastapi import APIRouter, Depends, status, HTTPException
from app.services.TTTService import NLLBTTTService

router = APIRouter(prefix="/translate", tags=["Translation"])

@router.post("/async-translate")
async def translate(
    text: str,
    source_lang: str,
    target_lang: str,
    nllb_service: NLLBTTTService
) -> dict:
    """Translate text from source language to target language."""
    try:
        result = await nllb_service.translate_async(text, source_lang, target_lang)
        return {"translation": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/normal-translate")
def translate_normal(
    text: str,
    source_lang: str,
    target_lang: str,
    nllb_service: NLLBTTTService
) -> dict:
    """Translate text from source language to target language."""
    try:
        result = nllb_service.translate(text, source_lang, target_lang)
        return {"translation": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))