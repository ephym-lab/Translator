from pydantic import BaseModel


class TranscriptionResult(BaseModel):
    """Result of a speech-to-text transcription."""

    text: str


class IntentResult(BaseModel):
    """Detected intent and any extracted entities."""

    intent: str
    entities: dict = {}


class PipelineResult(BaseModel):
    """Full result of a single voice assistant pipeline cycle."""

    transcript: str
    intent: str
    response: str


class SynthesizeRequest(BaseModel):
    """Request body for the /synthesize endpoint."""

    text: str
    voice: str = "en-US-JennyNeural"
