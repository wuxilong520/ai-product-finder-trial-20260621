from __future__ import annotations

from app.core.config import settings
from app.core.config_center import config_center
from app.core.environment_manager import environment_manager
from app.core.feedback_loop_v2 import feedback_loop_v2
from app.core.launch_checklist_engine import launch_checklist_engine


class ProductionDetector:
    def detect(self) -> dict:
        payment = config_center.payment()
        smtp = config_center.smtp()
        checklist = launch_checklist_engine.evaluate()
        flags = config_center.feature_flags()
        growth = feedback_loop_v2.metrics()
        return {
            "environment": environment_manager.current(),
            "payment_configured": bool(payment.get("wechat_pay_app_id") and payment.get("wechat_pay_mch_id") and payment.get("wechat_pay_api_v3_key") and payment.get("wechat_pay_private_key")),
            "email_configured": bool(smtp.get("host") and smtp.get("user") and smtp.get("password") and smtp.get("port")),
            "ssl_enabled": bool(str(settings.frontend_url).startswith("https://") and str(settings.backend_url).startswith("https://")),
            "database_state": "ready" if checklist["checks"].get("role_security_correct") else "blocked",
            "mock_status": "clean" if checklist["checks"].get("mock_data_removed") else "dirty",
            "trust_score": float(growth.get("ai_decision_accuracy") or 0.0),
            "execution_success_rate": float(growth.get("execution_success_rate") or 0.0),
        }


production_detector = ProductionDetector()
