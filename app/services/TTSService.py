from abc import ABC, abstractmethod
import asyncio
import os
import tempfile

import edge_tts
import pygame

from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseTTSService(ABC):
    """Abstract base class for Text-to-Speech services."""

    @abstractmethod
    async def synthesize(self, text: str, output_path: str) -> None:
        """
        Convert text to speech and save to a file.

        Args:
            text: Text to synthesize
            output_path: Path where the audio file will be saved (MP3)
        """
        ...

    @abstractmethod
    async def speak(self, text: str) -> None:
        """
        Synthesize text and play it immediately (blocking).

        Args:
            text: Text to speak aloud
        """
        ...


class EdgeTTSService(BaseTTSService):
    """
    Text-to-Speech service using Microsoft Edge-TTS neural voices.

    Requires an internet connection for synthesis.
    Uses pygame for cross-platform audio playback.
    """

    def __init__(self, voice: str = "en-US-JennyNeural"):
        self.voice = voice

    async def synthesize(self, text: str, output_path: str) -> None:
        """
        Convert text to speech and save as an MP3 file.

        Args:
            text: Text string to synthesize
            output_path: Destination file path (should end in .mp3)
        """
        logger.info(f"Synthesizing with voice '{self.voice}': \"{text}\"")
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        logger.info(f"Audio saved → {output_path}")

    async def speak(self, text: str) -> None:
        """
        Synthesize and immediately play the given text.

        Saves to a temporary MP3 file, plays it via pygame, then cleans up.

        Args:
            text: Text to speak aloud
        """
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name

        try:
            await self.synthesize(text, tmp_path)
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            pygame.mixer.quit()
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
