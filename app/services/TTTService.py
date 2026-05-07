from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from abc import ABC, abstractmethod

from app.utils.logger import get_logger

logger = get_logger(__name__)

class BaseTTTService(ABC):
    """Abstract base class for Text-to-Text Transfer Transformer (T3) services."""

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., "eng_Latn")
            target_lang: Target language code (e.g., "swh_Latn")

        Returns:
            str: Translated text
        """
        ...

class NLLBTTTService(BaseTTTService):
    """
    Offline Text-to-Text Transfer Transformer service using NLLB.

    Supports multiple languages with fair performance on consumer hardware.
    """

    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self.language_code_dic = {
            'english':'eng_Latn',
            'swahili':'swh_Latn',
            'kikuyu':'kik_Latn',
            'maasai':'mas_Latn',
            'somali':'som_Latn'
        }

    def _load_model(self) -> None:
        """Load the NLLB model and tokenizer if not already loaded."""
        if self._model is None or self._tokenizer is None:
            logger.info(f"Loading NLLB model: {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            logger.info("NLLB model loaded.")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using NLLB.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., "eng_Latn")
            target_lang: Target language code (e.g., "swh_Latn")

        Returns:
            str: Translated text

        Raises:
            RuntimeError: If model fails to load or process text
        """
        self._load_model()
        
        # Set source language as prefix
        self._tokenizer.src_lang = source_lang
        
        logger.info(f"Translating from {source_lang} to {target_lang}: '{text}'")
        
        # Tokenize input with explicit source language
        inputs = self._tokenizer(text, return_tensors="pt")
        
        # Set target language
        translated_tokens = self._model.generate(
            **inputs,
            forced_bos_token_id=self._tokenizer.convert_tokens_to_ids(target_lang)
        )
        
        # Decode output
        result = self._tokenizer.batch_decode(
            translated_tokens,
            skip_special_tokens=True
        )
        
        clean_text = result[0].strip()
        logger.info(f"Translated text: '{clean_text}'")
        
        return clean_text