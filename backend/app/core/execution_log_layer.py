from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime


class ExecutionLogLayer:
    def __init__(self) -> None:
        self._logs: dict[str, list[dict]] = defaultdict(list)

    def write(
        self,
        *,
        keyword: str,
        market: str,
        decision: dict,
        execution_level: str,
        blocked_reason: str,
        override_history: list[dict],
        platform_action: str = "",
        success: bool = False,
        rollback_reason: str = "",
        platform_execution_status: str = "blocked",
        execution_queue_status: str = "idle",
        channel: str = "",
        shop_domain: str = "",
        shopify_product_id: str = "",
        publish_receipt: dict | None = None,
    ) -> dict:
        key = f"{market}:{keyword}".lower()
        payload = {
            "created_at": datetime.now(UTC).isoformat(),
            "keyword": keyword,
            "market": market,
            "decision": decision,
            "execution_level": execution_level,
            "blocked_reason": blocked_reason,
            "override_history": override_history,
            "platform_action": platform_action,
            "success": success,
            "rollback_reason": rollback_reason,
            "platform_execution_status": platform_execution_status,
            "execution_queue_status": execution_queue_status,
            "channel": channel,
            "shop_domain": shop_domain,
            "shopify_product_id": shopify_product_id,
            "publish_receipt": publish_receipt or {},
        }
        self._logs[key].append(payload)
        return payload

    def get_logs(self, *, keyword: str, market: str) -> list[dict]:
        return list(self._logs.get(f"{market}:{keyword}".lower(), []))

    def list_logs(self) -> list[dict]:
        items: list[dict] = []
        for group in self._logs.values():
            items.extend(group)
        return items


execution_log_layer = ExecutionLogLayer()
