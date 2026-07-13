from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.core.runtime import AppError


class TokenEncryption:
    def _cipher(self) -> Fernet:
        raw_key = str(settings.token_encryption_key or "").strip()
        if not raw_key:
            raise AppError("TOKEN_ENCRYPTION_KEY_MISSING", "缺少 TOKEN_ENCRYPTION_KEY，无法安全保存平台 token", "security", 500)
        try:
            return Fernet(raw_key.encode("utf-8"))
        except Exception as exc:
            raise AppError("TOKEN_ENCRYPTION_KEY_INVALID", "TOKEN_ENCRYPTION_KEY 格式无效", "security", 500) from exc

    def encrypt(self, value: str) -> str:
        if not str(value or "").strip():
            return ""
        return self._cipher().encrypt(str(value).encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str) -> str:
        if not str(value or "").strip():
            return ""
        try:
            return self._cipher().decrypt(str(value).encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise AppError("TOKEN_DECRYPT_FAILED", "平台 token 解密失败", "security", 500) from exc


token_encryption = TokenEncryption()
