from abc import ABC, abstractmethod
import os

from app.services.STTService import BaseSTTService
from app.services.TTSService import BaseTTSService
from app.services.IntentService import BaseIntentService
from app.services.FunctionService import BaseFunctionService
from app.services.AudioInputService import BaseAudioInputService
from app.schemas.voice import IntentResult, PipelineResult
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BasePipelineService(ABC):
    """Abstract base class for the full voice assistant pipeline."""

    @abstractmethod
    async def run_once(self) -> PipelineResult:
        """
        Execute a single pipeline cycle:
        record → STT → intent → function → template → TTS → playback.

        Returns:
            PipelineResult: transcript, intent, and response for this cycle
        """
        ...

    @abstractmethod
    async def run_loop(self) -> None:
        """Run the pipeline continuously until EXIT intent or KeyboardInterrupt."""
        ...


class VoiceAssistantPipeline(BasePipelineService):
    """
    Full voice assistant pipeline orchestrator.

    Composes five modular services:
        AudioInput → STT → IntentDetection → FunctionExecution → TTS

    Each service is injected via the constructor for easy swapping and testing.
    All steps are logged via the shared logger utility.

    Response templates follow fixed, predefined formats — no free-form generation.
    """

    RESPONSE_TEMPLATES: dict[str, str] = {
        "GREETING": "Hello! How can I help you?",
        "WEATHER":  "The weather in {location} is {condition} with a temperature of {temp}°C.",
        "TIME":     "The current time is {time}.",
        "EXIT":     "Goodbye!",
        "FALLBACK": "Sorry, I didn't understand that. Please try again.",
    }

    def __init__(
        self,
        audio_input: BaseAudioInputService,
        stt: BaseSTTService,
        intent: BaseIntentService,
        functions: BaseFunctionService,
        tts: BaseTTSService,
    ):
        self.audio_input = audio_input
        self.stt = stt
        self.intent = intent
        self.functions = functions
        self.tts = tts

    async def run_once(self) -> PipelineResult:
        """
        Execute one complete voice interaction cycle.

        Steps:
            1. Record from microphone → WAV file
            2. Whisper STT → clean transcript
            3. Rule-based intent detection → intent + entities
            4. Function execution → data (weather/time/etc.)
            5. Fill response template
            6. Edge-TTS synthesis + playback

        Returns:
            PipelineResult: Full result of this interaction cycle
        """
        audio_path = self.audio_input.record()

        try:
            # Step 1: Speech → Text
            transcript = self.stt.transcribe(audio_path)
            logger.info(f'[STT]    → "{transcript}"')

            # Step 2: Intent detection
            intent_result = self.intent.detect(transcript)
            logger.info(f"[INTENT] → {intent_result.intent} | entities: {intent_result.entities}")

            # Step 3: Execute function and fill template
            response = await self._build_response(intent_result)
            logger.info(f'[RESP]   → "{response}"')

            # Step 4: Speak the response
            await self.tts.speak(response)

            return PipelineResult(
                transcript=transcript,
                intent=intent_result.intent,
                response=response,
            )

        finally:
            # Always clean up the temp audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

    async def _build_response(self, intent_result: IntentResult) -> str:
        """
        Execute the appropriate function and fill the response template.

        Args:
            intent_result: Detected intent and entities from IntentService

        Returns:
            str: Ready-to-speak response string
        """
        intent = intent_result.intent
        entities = intent_result.entities

        if intent == "WEATHER":
            location = entities.get("location", settings.DEFAULT_LOCATION)
            weather = await self.functions.get_weather(location)
            return self.RESPONSE_TEMPLATES["WEATHER"].format(
                location=weather["location"],
                condition=weather["condition"],
                temp=weather["temp"],
            )

        elif intent == "TIME":
            return self.RESPONSE_TEMPLATES["TIME"].format(
                time=self.functions.get_time()
            )

        elif intent == "EXIT":
            self.functions.end_session()
            return self.RESPONSE_TEMPLATES["EXIT"]

        elif intent == "GREETING":
            return self.RESPONSE_TEMPLATES["GREETING"]

        else:
            return self.RESPONSE_TEMPLATES["FALLBACK"]

    async def run_loop(self) -> None:
        """
        Run the assistant in a continuous loop until EXIT or KeyboardInterrupt.

        Prints a formatted summary of each cycle to stdout.
        Exits cleanly on EXIT intent or Ctrl+C.
        """
        print("\n" + "=" * 55)
        print("  Voice Assistant — Ready")
        print("  Speak after the prompt. Press Ctrl+C to quit.")
        print("=" * 55 + "\n")

        while True:
            try:
                print("─" * 40)
                print("Listening...")
                result = await self.run_once()

                print(f'Transcript : "{result.transcript}"')
                print(f"Intent     : {result.intent}")
                print(f'Response   : "{result.response}"\n')

                if self.functions.should_exit:
                    print("Session ended. Goodbye!")
                    break

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                print(f"Error: {e}. Retrying...\n")
