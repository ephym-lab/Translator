#!/usr/bin/env python3
"""
Voice Assistant CLI
===================
Standalone entry point for the voice assistant pipeline.

Usage:
    uv run python cli.py              # default: mic input, 5s recording
    uv run python cli.py --duration 8 # custom recording duration
    uv run python cli.py --model tiny  # use a smaller/faster Whisper model

Press Ctrl+C at any time to exit cleanly.
"""
import argparse
import asyncio
import sys

from app.core.config import settings
from app.services.AudioInputService import MicrophoneInputService
from app.services.FunctionService import VoiceFunctionService
from app.services.IntentService import RuleBasedIntentService
from app.services.PipelineService import VoiceAssistantPipeline
from app.services.STTService import WhisperSTTService
from app.services.TTSService import EdgeTTSService
from app.utils.logger import get_logger

logger = get_logger("cli")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Voice Assistant — modular STT → intent → TTS pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python cli.py
  uv run python cli.py --duration 8
  uv run python cli.py --model tiny
  uv run python cli.py --voice en-GB-SoniaNeural
        """,
    )
    parser.add_argument(
        "--model",
        default=settings.WHISPER_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help=f"Whisper model size (default: {settings.WHISPER_MODEL})",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=settings.MIC_DURATION,
        help=f"Recording duration in seconds (default: {settings.MIC_DURATION})",
    )
    parser.add_argument(
        "--voice",
        default=settings.TTS_VOICE,
        help=f"Edge-TTS voice name (default: {settings.TTS_VOICE})",
    )
    return parser.parse_args()


def build_pipeline(args: argparse.Namespace) -> VoiceAssistantPipeline:
    """Compose and return the pipeline with CLI-provided settings."""
    return VoiceAssistantPipeline(
        audio_input=MicrophoneInputService(
            sample_rate=settings.MIC_SAMPLE_RATE,
            duration=args.duration,
        ),
        stt=WhisperSTTService(model_name=args.model),
        intent=RuleBasedIntentService(),
        functions=VoiceFunctionService(),
        tts=EdgeTTSService(voice=args.voice),
    )


async def main() -> None:
    args = parse_args()

    print()
    print("┌─────────────────────────────────────────────────────┐")
    print("│        🤖  Voice Assistant — CLI Mode               │")
    print("├─────────────────────────────────────────────────────┤")
    print(f"│  Whisper model : {args.model:<36}│")
    print(f"│  Recording     : {args.duration}s per utterance{' ' * (27 - len(str(args.duration)))}│")
    print(f"│  TTS voice     : {args.voice:<36}│")
    print("├─────────────────────────────────────────────────────┤")
    print("│  Supported intents:                                 │")
    print("│    GREETING · WEATHER · TIME · EXIT                 │")
    print("└─────────────────────────────────────────────────────┘")
    print()

    pipeline = build_pipeline(args)
    await pipeline.run_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
