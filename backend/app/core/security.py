from datetime import UTC, datetime, timedelta
import secrets

import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.runtime import AppError
from app.core.token_encryption import token_encryption


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | int, expires_delta: timedelta | None = None, extra_payload: dict | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": str(subject), "exp": expire, "jti": secrets.token_urlsafe(16)}
    if extra_payload:
        payload.update(extra_payload)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str | int, expires_delta: timedelta | None = None, extra_payload: dict | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(days=30))
    payload = {"sub": str(subject), "exp": expire, "token_type": "refresh", "jti": secrets.token_urlsafe(24)}
    if extra_payload:
        payload.update(extra_payload)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError as exc:
        raise AppError("TOKEN_INVALID", "Token 已失效或无效", "auth", 401) from exc


def encrypt_token(value: str) -> str:
    return token_encryption.encrypt(value)


def decrypt_token(value: str) -> str:
    return token_encryption.decrypt(value)
