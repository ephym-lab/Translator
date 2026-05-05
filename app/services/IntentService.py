from abc import ABC, abstractmethod
import re

from app.schemas.voice import IntentResult
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseIntentService(ABC):
    """Abstract base class for intent detection services."""

    @abstractmethod
    def detect(self, text: str) -> IntentResult:
        """
        Detect intent and extract entities from transcribed text.

        Args:
            text: Clean transcribed text from STT

        Returns:
            IntentResult: Detected intent and any extracted entities
        """
        ...


class RuleBasedIntentService(BaseIntentService):
    """
    Keyword-matching intent detector with basic entity extraction.

    No machine learning or LLMs — pure if-else keyword logic.

    Supported intents:
        GREETING  → hello, hi, hey, greetings, howdy
        WEATHER   → weather, temperature, forecast, humid, rain, sunny, hot, cold
        TIME      → time, clock, what time, current time
        EXIT      → exit, stop, goodbye, bye, quit, see you
        FALLBACK  → no keyword match
    """

    KEYWORD_MAP: dict[str, list[str]] = {
        "GREETING": ["hello", "hi", "hey", "greetings", "howdy", "good morning", "good evening"],
        "WEATHER": [
            "weather", "temperature", "forecast", "humid",
            "rain", "sunny", "hot", "cold", "wind", "snow",
        ],
        "TIME": ["time", "clock", "what time", "current time", "hour"],
        "EXIT": ["exit", "stop", "goodbye", "bye", "quit", "see you", "farewell"],
    }

    def detect(self, text: str) -> IntentResult:
        """
        Match text against keyword lists in priority order.

        Args:
            text: Input text (will be lowercased internally)

        Returns:
            IntentResult: First matching intent and extracted entities,
                          or FALLBACK if no match found
        """
        normalized = text.lower().strip()

        for intent, keywords in self.KEYWORD_MAP.items():
            for keyword in keywords:
                if keyword in normalized:
                    entities: dict = {}
                    if intent == "WEATHER":
                        entities["location"] = self._extract_location(normalized)

                    logger.debug(f"Matched keyword '{keyword}' → intent: {intent}")
                    return IntentResult(intent=intent, entities=entities)

        return IntentResult(intent="FALLBACK", entities={})

    def _extract_location(self, text: str) -> str:
        """
        Extract a location name from the input text using regex patterns.

        Tries patterns like:
            "weather in London"
            "temperature at Paris"
            "London weather"
            "forecast for Nairobi"

        Args:
            text: Lowercased input text

        Returns:
            str: Title-cased location, or the configured default if not found
        """
        patterns = [
            r"(?:in|at|for|near)\s+([a-z][a-z\s]{1,28})(?:\s+(?:today|tomorrow|now|please)|[\?.,]|$)",
            r"([a-z][a-z\s]{1,20}?)\s+(?:weather|temperature|forecast)",
        ]

        noise_words = {"the", "my", "our", "current", "local", "today", "what", "is", "now"}

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip().title()
                if location.lower() not in noise_words and len(location) > 1:
                    return location

        return settings.DEFAULT_LOCATION
