from pydantic import BaseModel

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class TranslationData(BaseModel):
    original: str
    translated: str
    source_lang: str
    target_lang: str

class TranslationResponse(BaseModel):
    message: str
    data: TranslationData

