from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Voice Assistant"
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "changeme-in-production"

    # --- STT ---
    WHISPER_MODEL: str = "base"  # tiny | base | small | medium | large

    # --- TTS ---
    TTS_VOICE: str = "en-US-JennyNeural"

    # --- Microphone ---
    MIC_SAMPLE_RATE: int = 16000
    MIC_DURATION: int = 5  # seconds to record per utterance

    # --- Weather API (open-meteo.com — free, no key required) ---
    WEATHER_API_BASE: str = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_API_BASE: str = "https://geocoding-api.open-meteo.com/v1/search"
    DEFAULT_LOCATION: str = "your area"

    class Config:
        env_file = ".env"


settings = Settings()
