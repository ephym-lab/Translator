from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Language Dataset Platform"
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""

    # --- JWT ---
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- OTP ---
    OTP_EXPIRE_MINUTES: int = 10

    # --- Gmail SMTP ---
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_APP_PASSWORD: str = ""
    EMAIL_FROM_NAME: str = "Language Dataset Platform"

    # --- Voice Assistant (STT / TTS / Mic) ---
    WHISPER_MODEL: str = "base"
    TTS_VOICE: str = "en-US-JennyNeural"
    MIC_SAMPLE_RATE: int = 16000
    MIC_DURATION: int = 5
    WEATHER_API_BASE: str = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_API_BASE: str = "https://geocoding-api.open-meteo.com/v1/search"
    DEFAULT_LOCATION: str = "Nairobi"
    # Postgres DB
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: int = 5432
    DB_HOST: str = ""

    #ai
    GROK_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
