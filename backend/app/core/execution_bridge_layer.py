from __future__ import annotations

from app.core.execution_queue import execution_queue
from app.core.feedback_loop_v2 import feedback_loop_v2
from app.integration.client_manager import client_manager
from app.core.commercial_readiness_engine import commercial_readiness_engine
from app.core.production_bootstrap_layer import production_bootstrap_layer
from app.core.platform_router import platform_router


class ExecutionBridgeLayer:
    def execute(
        self,
        *,
        decision: dict,
        listing_bundle: dict | None = None,
        publish_payload: dict | None = None,
    ) -> dict:
        action_level = str(decision.get("action_level", "WATCH")).upper()
        channel = str((publish_payload or {}).get("channel") or (listing_bundle or {}).get("listing", {}).get("channel") or "shopify")
        keyword = str(decision.get("keyword", ""))
        market = str(decision.get("market", ""))

        readiness = commercial_readiness_engine.evaluate()
        bootstrap_status = production_bootstrap_layer.status()
        product_mode = bootstrap_status["product_mode"]
        if product_mode != "production_mode" and action_level in {"SCALE", "AUTO_LIST"}:
            action_level = "WATCH"
        mapping = self._map_action(action_level)
        platform_status = {
            "action_level": action_level,
            "execution_bridge_mapping": mapping,
            "platform_execution_status": "blocked",
            "execution_queue_status": "idle",
            "platform_action": mapping["platform_action"],
            "success": False,
            "rollback_reason": "",
            "product_mode": product_mode,
            "execution_target_platform": platform_router.decide_platform_target(action_level=action_level),
        }

        if not bool(decision.get("execution_allowed")):
            platform_status["platform_execution_status"] = "blocked"
            platform_status["rollback_reason"] = decision.get("execution_block_reason") or "执行控制层禁止执行"
            return platform_status

        if action_level == "WATCH":
            platform_status["platform_execution_status"] = "blocked"
            platform_status["success"] = True
            platform_status["rollback_reason"] = "当前等级为 WATCH，只记录，不执行平台动作"
            return platform_status

        if action_level == "TEST":
            execution_queue.queue_test({"keyword": keyword, "market": market, "decision": decision})
            platform_action_result = platform_router.execute_platform_action(
                action_level=action_level,
                product=((listing_bundle or {}).get('listing') or {'title': keyword, 'price': decision.get('recommended_price', 0), 'supplier': 'unknown', 'availability': True, 'shipping_time': '', 'raw_platform': 'shopify'})
            )
            platform_status["platform_execution_status"] = "queued_test"
            platform_status["execution_queue_status"] = "queue_test"
            platform_status["success"] = True
            platform_status["platform_action_result"] = platform_action_result
            return platform_status

        if action_level == "SCALE":
            execution_queue.queue_batch({"keyword": keyword, "market": market, "decision": decision})
            platform_status["platform_execution_status"] = "queued_batch"
            platform_status["execution_queue_status"] = "queue_batch"
            platform_status["success"] = True
            return platform_status

        if action_level == "AUTO_LIST":
            execution_queue.queue_auto({"keyword": keyword, "market": market, "decision": decision})
            adapter = client_manager.get_execution_client(channel=channel)
            platform_action_result = platform_router.execute_platform_action(
                action_level=action_level,
                product=((listing_bundle or {}).get('listing') or {'title': keyword, 'price': decision.get('recommended_price', 0), 'supplier': 'unknown', 'availability': True, 'shipping_time': '', 'raw_platform': 'shopify'})
            )
            platform_status["platform_execution_status"] = f"auto_publish_ready:{adapter.adapter_name}"
            platform_status["execution_queue_status"] = "queue_auto"
            platform_status["success"] = True
            platform_status["platform_action_result"] = platform_action_result
            return platform_status

        platform_status["rollback_reason"] = "未命中可执行动作"
        return platform_status

    def _map_action(self, action_level: str) -> dict:
        if action_level == "KILL":
            return {"platform_action": "block_listing", "publish_allowed": False}
        if action_level == "WATCH":
            return {"platform_action": "log_only", "publish_allowed": False}
        if action_level == "TEST":
            return {"platform_action": "small_batch_listing", "publish_allowed": True}
        if action_level == "SCALE":
            return {"platform_action": "batch_publish", "publish_allowed": True}
        if action_level == "AUTO_LIST":
            return {"platform_action": "auto_publish_all_platforms", "publish_allowed": True}
        return {"platform_action": "unknown", "publish_allowed": False}

    def on_platform_result(self, result: dict) -> dict:
        status = str(result.get("status") or "failed").lower()
        success_map = {
            "success": 1.0,
            "failed": 0.0,
            "partial success": 0.5,
            "partial_success": 0.5,
        }
        publish_success_rate = success_map.get(status, 0.0)
        payload = feedback_loop_v2.record(
            decision_id=str(result.get("decision_id") or "unknown"),
            keyword=str(result.get("keyword") or "unknown"),
            market=str(result.get("market") or "unknown"),
            listing_result=str(result.get("listing_result") or status),
            publish_success_rate=publish_success_rate,
            conversion_rate=float(result.get("conversion_rate") or 0.0),
            profit_actual=float(result.get("profit_actual") or 0.0),
            profit_predicted=float(result.get("profit_predicted") or 0.0),
            platform_performance=dict(result.get("platform_performance") or {"status": status}),
        )
        return payload


execution_bridge_layer = ExecutionBridgeLayer()
