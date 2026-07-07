from __future__ import annotations

from app.core.config import settings


class ConfigCenter:
    def smtp(self) -> dict:
        return {
            "host": settings.smtp_host,
            "port": settings.smtp_port,
            "user": settings.smtp_user,
            "password": settings.smtp_password,
            "from_email": settings.smtp_from_email or settings.smtp_user,
            "use_tls": settings.smtp_use_tls,
            "use_ssl": settings.smtp_use_ssl,
        }

    def payment(self) -> dict:
        return {
            "wechat_pay_app_id": settings.wechat_pay_app_id,
            "wechat_pay_mch_id": settings.wechat_pay_mch_id,
            "wechat_pay_api_v3_key": settings.wechat_pay_api_v3_key,
            "wechat_pay_private_key": settings.wechat_pay_private_key,
        }

    def ai_models(self) -> dict:
        return {
            "openai_model": settings.openai_model,
            "openai_base_url": settings.openai_base_url,
        }

    def feature_flags(self) -> dict:
        return {
            "mock_ai_enabled": settings.mock_ai_enabled,
            "mock_crawler_enabled": settings.mock_crawler_enabled,
        }


config_center = ConfigCenter()
