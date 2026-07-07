from __future__ import annotations

from app.core.commercial_readiness_engine import commercial_readiness_engine
from app.core.environment_manager import environment_manager
from app.core.production_detector import production_detector


class ProductionBlockedError(Exception):
    def __init__(self, blocking_items: list[str]):
        self.blocking_items = blocking_items
        super().__init__("生产切换条件未满足")


class ProductionBootstrapLayer:
    def __init__(self) -> None:
        self._product_mode_override: str | None = None

    def status(self) -> dict:
        readiness = commercial_readiness_engine.evaluate()
        detected = production_detector.detect()
        product_mode = self._product_mode_override or readiness["product_mode"]
        blocking_items = self._build_blocking_items(readiness=readiness, detected=detected)
        production_ready = len(blocking_items) == 0
        return {
            "product_mode": product_mode,
            "production_ready": production_ready,
            "blocking_items": blocking_items,
            "can_switch_to_production": production_ready,
            "system_bootstrap_status": "ready" if production_ready else "blocked",
            "detector": detected,
        }

    def activate_production(self) -> dict:
        status = self.status()
        if not status["production_ready"]:
            raise ProductionBlockedError(status["blocking_items"])
        self._product_mode_override = "production_mode"
        status["product_mode"] = "production_mode"
        status["system_bootstrap_status"] = "activated"
        status["can_switch_to_production"] = True
        return status

    def current_mode(self) -> str:
        return self._product_mode_override or commercial_readiness_engine.evaluate()["product_mode"]

    def _build_blocking_items(self, *, readiness: dict, detected: dict) -> list[str]:
        items: list[str] = []
        if not detected["email_configured"]:
            items.append("SMTP 未配置完成")
        if not detected["ssl_enabled"]:
            items.append("HTTPS 未启用")
        if not detected["payment_configured"]:
            items.append("支付未配置完成")
        if detected["mock_status"] != "clean":
            items.append("mock 数据未清理")
        if float(detected["trust_score"]) <= 0.8:
            items.append("TRUST_SCORE 未超过 0.8")
        if str(readiness["risk_level"]).lower() != "low":
            items.append("RISK_LEVEL 不是 low")
        if environment_manager.current() != "production":
            items.append("当前环境不是 production")
        return items


production_bootstrap_layer = ProductionBootstrapLayer()
