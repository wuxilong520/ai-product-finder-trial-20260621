from __future__ import annotations

from app.core.config import settings
from app.core.runtime import AppError


class AmazonOAuthService:
    def build_authorize_url(self) -> dict:
        if not str(settings.amazon_oauth_client_id or "").strip() or not str(settings.amazon_oauth_redirect_uri or "").strip():
            raise AppError("AMAZON_OAUTH_NOT_CONFIGURED", "缺少 Amazon OAuth 配置", "oauth", 500)
        return {
            "platform": "amazon",
            "authorize_url": "https://sellercentral.amazon.com/apps/authorize/consent",
            "status": "reserved",
        }


amazon_oauth_service = AmazonOAuthService()
