from __future__ import annotations

from app.core.config import settings
from app.core.runtime import AppError


class TikTokOAuthService:
    def build_authorize_url(self) -> dict:
        if not str(settings.tiktok_app_id or "").strip() or not str(settings.tiktok_oauth_redirect_uri or "").strip():
            raise AppError("TIKTOK_OAUTH_NOT_CONFIGURED", "缺少 TikTok OAuth 配置", "oauth", 500)
        return {
            "platform": "tiktok",
            "authorize_url": "https://business-api.tiktok.com/portal/auth",
            "status": "reserved",
        }


tiktok_oauth_service = TikTokOAuthService()
