from fastapi import APIRouter, Depends, status, HTTPException
from app.services.TTTService import NLLBTTTService
from app.schemas.translator import TranslationRequest, TranslationResponse,TranslationData
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/translate", tags=["Translation"])

#load model once and reuse
_nllb_service = NLLBTTTService()

def get_nllb_service() -> NLLBTTTService:
    return _nllb_service

@router.post("/async-translate",response_model=TranslationResponse,status_code=status.HTTP_200_OK)
async def translate(
    data: TranslationRequest, 
    nllb_service: NLLBTTTService = Depends(get_nllb_service),
    _:User= Depends(get_current_user)
) -> dict:
    """Translate text from source language to target language."""
    try:
        result = await nllb_service.translate_async(data.text, data.source_lang, data.target_lang)
        return TranslationResponse(
            message="Translation successful",
            data=TranslationData(
                original=data.text,
                translated=result,
                source_lang=data.source_lang,
                target_lang=data.target_lang,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/normal-translate",response_model=TranslationResponse,status_code=status.HTTP_200_OK)
def translate_normal(
    data: TranslationRequest,
    nllb_service: NLLBTTTService = Depends(get_nllb_service),
    _:User = Depends(get_current_user)
) -> dict:
    """Translate text from source language to target language."""
    try:
        result = nllb_service.translate(data.text, data.source_lang, data.target_lang)
        return TranslationResponse(
            message="Translation successful",
            data=TranslationData(
                original=data.text,
                translated=result,
                source_lang=data.source_lang,
                target_lang=data.target_lang,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))   