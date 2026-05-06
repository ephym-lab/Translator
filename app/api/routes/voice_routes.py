import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.voice import PipelineResult, SynthesizeRequest, TranscriptionResult
from app.services.AudioInputService import MicrophoneInputService, BaseAudioInputService
from app.services.FunctionService import VoiceFunctionService
from app.services.IntentService import RuleBasedIntentService
from app.services.PipelineService import VoiceAssistantPipeline
from app.services.STTService import WhisperSTTService
from app.services.TTSService import EdgeTTSService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

# Supported audio formats 
SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}


#Dependency factories


def get_stt() -> WhisperSTTService:
    return WhisperSTTService(model_name=settings.WHISPER_MODEL)


def get_tts() -> EdgeTTSService:
    return EdgeTTSService(voice=settings.TTS_VOICE)


def get_pipeline() -> VoiceAssistantPipeline:
    return VoiceAssistantPipeline(
        audio_input=MicrophoneInputService(),
        stt=WhisperSTTService(model_name=settings.WHISPER_MODEL),
        intent=RuleBasedIntentService(),
        functions=VoiceFunctionService(),
        tts=EdgeTTSService(voice=settings.TTS_VOICE),
    )


# Endpoints 

@router.post(
    "/transcribe",
    response_model=TranscriptionResult,
    summary="Transcribe audio to text",
    description="Upload an audio file and receive its transcribed text via Whisper.",
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, M4A, OGG, FLAC)"),
    stt: WhisperSTTService = Depends(get_stt),
) -> TranscriptionResult:
    """
    Transcribe an uploaded audio file to plain text.

    Args:
        file: Audio file to transcribe
        stt: Injected WhisperSTTService

    Returns:
        TranscriptionResult: The transcribed text

    Raises:
        HTTPException 400: Unsupported audio format
    """
    suffix = os.path.splitext(file.filename or "")[1].lower()
    if suffix not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{suffix}'. Supported: {', '.join(SUPPORTED_FORMATS)}",
        )

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        text = stt.transcribe(tmp_path)
        return TranscriptionResult(text=text)
    finally:
        os.remove(tmp_path)


@router.post(
    "/process",
    response_model=PipelineResult,
    summary="Run full voice pipeline",
    description=(
        "Upload an audio file and run it through the full pipeline: "
        "STT → intent detection → function → response template. "
        "Returns the transcript, detected intent, and spoken response."
    ),
)
async def process_audio(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, M4A, OGG, FLAC)"),
) -> PipelineResult:
    """
    Run an uploaded audio file through the complete voice assistant pipeline.

    Args:
        file: Audio file containing a voice command

    Returns:
        PipelineResult: Transcript, intent, and response text

    Raises:
        HTTPException 400: Unsupported audio format
    """
    suffix = os.path.splitext(file.filename or "")[1].lower()
    if suffix not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{suffix}'. Supported: {', '.join(SUPPORTED_FORMATS)}",
        )

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Inject a file-based audio source — bypass the microphone
    class _FileAudioInput(BaseAudioInputService):
        def record(self, duration=None):  # type: ignore[override]
            return tmp_path

    pipeline = VoiceAssistantPipeline(
        audio_input=_FileAudioInput(),
        stt=WhisperSTTService(model_name=settings.WHISPER_MODEL),
        intent=RuleBasedIntentService(),
        functions=VoiceFunctionService(),
        tts=EdgeTTSService(voice=settings.TTS_VOICE),
    )

    try:
        # Don't play audio over the server's speakers — override speak()
        pipeline.tts.speak = lambda text: None  # type: ignore[method-assign]
        result = await pipeline.run_once()
        return result
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post(
    "/synthesize",
    summary="Text to speech",
    description="Convert text to an MP3 audio file using Edge-TTS neural voice.",
    response_class=FileResponse,
)
async def synthesize_text(
    body: SynthesizeRequest,
    tts: EdgeTTSService = Depends(get_tts),
) -> FileResponse:
    """
    Synthesize the given text to speech and return an MP3 file.

    Args:
        body: Text to synthesize and optional voice name
        tts: Injected EdgeTTSService

    Returns:
        FileResponse: MP3 audio file download
    """
    tmp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_path = tmp_file.name
    tmp_file.close()

    tts.voice = body.voice
    await tts.synthesize(body.text, tmp_path)

    return FileResponse(
        path=tmp_path,
        media_type="audio/mpeg",
        filename="response.mp3",
    )
