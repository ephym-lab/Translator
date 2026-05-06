import random
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#Password

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ─── JWT ─────────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """Create a short-lived JWT access token."""
    payload = data.copy()
    payload.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    })
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token."""
    payload = data.copy()
    payload.update({
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
    })
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and return JWT payload. Raises JWTError on invalid/expired tokens."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


# ─── OTP ─────────────────────────────────────────────────────────────────────

def generate_otp() -> str:
    """Generate a 6-digit numeric OTP code."""
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, code: str) -> None:
    """
    Stub: In production, integrate SendGrid / SES / SMTP here.
    During development the OTP is returned directly in the API response.
    """
    pass
