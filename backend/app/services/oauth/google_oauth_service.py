from __future__ import annotations

from app.core.config import settings
from app.core.runtime import AppError


class GoogleOAuthService:
    def build_authorize_url(self) -> dict:
        if not str(settings.google_ads_client_id or "").strip() or not str(settings.google_oauth_redirect_uri or "").strip():
            raise AppError("GOOGLE_OAUTH_NOT_CONFIGURED", "缺少 Google OAuth 配置", "oauth", 500)
        return {
            "platform": "google_ads",
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "status": "reserved",
        }


google_oauth_service = GoogleOAuthService()
