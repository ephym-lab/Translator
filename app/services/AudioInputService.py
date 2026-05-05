from abc import ABC, abstractmethod
import os
import tempfile

import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAudioInputService(ABC):
    """Abstract base class for audio input capture."""

    @abstractmethod
    def record(self, duration: int | None = None) -> str:
        """
        Record audio from an input source.

        Args:
            duration: Recording length in seconds (uses default if None)

        Returns:
            str: Absolute path to the saved WAV file
        """
        ...


class MicrophoneInputService(BaseAudioInputService):
    """
    Captures audio from the system's default microphone.

    Uses sounddevice for recording and scipy for WAV serialization.
    Audio is saved to a temporary file that the caller is responsible
    for deleting after use.
    """

    def __init__(
        self,
        sample_rate: int | None = None,
        duration: int | None = None,
    ):
        self.sample_rate = sample_rate or settings.MIC_SAMPLE_RATE
        self.default_duration = duration or settings.MIC_DURATION

    def record(self, duration: int | None = None) -> str:
        """
        Record from the default microphone and save as a WAV file.

        Args:
            duration: Override the default recording duration (seconds)

        Returns:
            str: Path to the temporary WAV file containing the recording

        Raises:
            sounddevice.PortAudioError: If no input device is available
        """
        record_duration = duration or self.default_duration
        logger.info(f"Recording for {record_duration}s (sample rate: {self.sample_rate}Hz)...")

        audio = sd.rec(
            int(record_duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
        )
        sd.wait()  # Block until recording is complete

        tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(tmp_file.name, self.sample_rate, audio)
        tmp_file.close()

        logger.info(f"Audio captured → {tmp_file.name}")
        return tmp_file.name
