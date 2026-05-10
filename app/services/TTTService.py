from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from abc import ABC, abstractmethod
import asyncio
from functools import partial
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseTTTService(ABC):
    """Abstract base class for Text-to-Text Transfer Transformer services."""

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str: ...


class NLLBTTTService(BaseTTTService):
    """Offline translation service using Facebook NLLB-200."""

    LANGUAGE_CODES = {
        "english": "eng_Latn",
        "swahili": "swh_Latn",
        "kikuyu":  "kik_Latn",
        "maasai":  "mas_Latn",
        "somali":  "som_Latn",
        "kalenjin":"kal_Latn",
        "meru":    "mer_Latn",
        "kamba":   "kam_Latn",
        "german":  "deu_Latn",
        "chinese": "zho_Hans",
        "french":  "fra_Latn",
        "russian": "rus_Cyrl",
        "spanish": "spa_Latn",
        "italian": "ita_Latn",
        "portuguese": "por_Latn",
        "japanese": "jpn_Jpan",
        "korean": "kor_Hang",
        "arabic": "ara_Arab",
        "hindi": "hin_Deva",
        "bengali": "ben_Beng",
        "punjabi": "pan_Guru",
        "urdu": "urd_Arab",
        "telugu": "tel_Telu",
        "marathi": "mar_Deva",
        "tamil": "tam_Taml",
        "dholuo":   "luo_Latn"

    }
    
    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None

    def _load_model(self) -> None:
        if self._model is None or self._tokenizer is None:
            logger.info(f"Loading NLLB model: {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            logger.info("NLLB model loaded successfully.")

    def get_language_code(self, lang: str) -> str:
        normalized = lang.lower().strip()
        code = self.LANGUAGE_CODES.get(normalized)
        if code is None:
            logger.warning(f"Unknown language '{lang}', falling back to English")
            return "eng_Latn"
        return code

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        self._load_model()

        src_code = self.get_language_code(source_lang)
        tgt_code = self.get_language_code(target_lang)

        logger.info(f"Translating [{src_code} → {tgt_code}]: '{text}'")

        try:
            self._tokenizer.src_lang = src_code
            inputs = self._tokenizer(text, return_tensors="pt")
            translated_tokens = self._model.generate(
                **inputs,
                forced_bos_token_id=self._tokenizer.convert_tokens_to_ids(tgt_code)
            )
            result = self._tokenizer.batch_decode(
                translated_tokens, skip_special_tokens=True
            )
            clean_text = result[0].strip()
            logger.info(f"Translation result: '{clean_text}'")
            return clean_text

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise RuntimeError(f"Translation failed: {e}") from e

    async def translate_async(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        """Non-blocking translation for use in FastAPI async routes."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(self.translate, text, source_lang, target_lang)
        )
        