from abc import ABC, abstractmethod

import whisper

from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseSTTService(ABC):
    """Abstract base class for Speech-to-Text services."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to clean text.

        Args:
            audio_path: Absolute path to the audio file (WAV, MP3, etc.)

        Returns:
            str: Cleaned transcribed text
        """
        ...


class WhisperSTTService(BaseSTTService):
    """
    Offline Speech-to-Text service powered by OpenAI Whisper.

    Lazy-loads the model on first use to avoid startup delay.
    Model is cached on disk by Whisper (~140 MB for 'base').
    """

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._model = None

    def _load_model(self) -> None:
        """Load the Whisper model if not already loaded."""
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self._model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded.")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to clean text using Whisper.

        Args:
            audio_path: Path to the audio file to transcribe

        Returns:
            str: Stripped, clean transcribed text

        Raises:
            FileNotFoundError: If the audio file does not exist
        """
        self._load_model()
        logger.info(f"Transcribing: {audio_path}")
        result = self._model.transcribe(audio_path, fp16=False)
        text = result["text"].strip()
        return text
