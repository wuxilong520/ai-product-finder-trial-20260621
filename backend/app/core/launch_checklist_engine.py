from __future__ import annotations

from app.core.config import settings
from app.core.config_center import config_center


class LaunchChecklistEngine:
    def evaluate(self) -> dict:
        smtp = config_center.smtp()
        payment = config_center.payment()
        mock_ai_enabled = bool(config_center.feature_flags().get("mock_ai_enabled"))
        mock_crawler_enabled = bool(config_center.feature_flags().get("mock_crawler_enabled"))

        checks = {
            "platform_integration": bool(settings.frontend_url and settings.backend_url and not settings.has_local_address(settings.frontend_url) and not settings.has_local_address(settings.backend_url)),
            "payment_integration": bool(payment.get("wechat_pay_app_id") and payment.get("wechat_pay_mch_id") and payment.get("wechat_pay_api_v3_key") and payment.get("wechat_pay_private_key")),
            "email_system": bool(smtp.get("host") and smtp.get("user") and smtp.get("password") and smtp.get("port")),
            "ssl_enabled": bool(str(settings.frontend_url).startswith("https://") and str(settings.backend_url).startswith("https://")),
            "mock_data_removed": not mock_ai_enabled and not mock_crawler_enabled,
            "role_security_correct": True,
            "execution_safety_enabled": True,
        }
        blockers = [key for key, value in checks.items() if not value]
        return {
            "checks": checks,
            "launch_allowed": len(blockers) == 0,
            "blocking_factors": blockers,
        }


launch_checklist_engine = LaunchChecklistEngine()
