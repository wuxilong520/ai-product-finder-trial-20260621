from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.audit_logger import audit_logger
from app.core.execution_bridge_layer import execution_bridge_layer
from app.core.execution_log_layer import execution_log_layer
from app.integration.client_manager import client_manager
from app.core.production_bootstrap_layer import production_bootstrap_layer
from app.services.listing_service import listing_service


class PublishServiceBase(ABC):
    @abstractmethod
    def publish(self, *, keyword: str, market: str, channel: str, shop_domain: str, oauth_code: str | None) -> dict:
        raise NotImplementedError


class PublishService(PublishServiceBase):
    def _write_execution_log(
        self,
        *,
        keyword: str,
        market: str,
        channel: str,
        shop_domain: str,
        decision: dict,
        blocked_reason: str,
        platform_action: str,
        success: bool,
        rollback_reason: str,
        platform_execution_status: str,
        execution_queue_status: str,
        shopify_product_id: str = "",
        publish_receipt: dict | None = None,
    ) -> None:
        execution_log_layer.write(
            keyword=keyword,
            market=market,
            decision=decision,
            execution_level=str(decision.get("action_level") or "WATCH"),
            blocked_reason=blocked_reason,
            override_history=list(decision.get("override_history") or []),
            platform_action=platform_action,
            success=success,
            rollback_reason=rollback_reason,
            platform_execution_status=platform_execution_status,
            execution_queue_status=execution_queue_status,
            channel=channel,
            shop_domain=shop_domain,
            shopify_product_id=shopify_product_id,
            publish_receipt=publish_receipt,
        )

    def publish(self, *, keyword: str, market: str, channel: str, shop_domain: str, oauth_code: str | None) -> dict:
        bootstrap_status = production_bootstrap_layer.status()
        if not bootstrap_status["production_ready"]:
            result = {
                "oauth": None,
                "listing": None,
                "publish": None,
                "shopify_product_id": None,
                "message": "系统还没有达到 production_ready，已锁死真实发布。",
                "platform_execution_status": "blocked",
                "execution_bridge_mapping": {"platform_action": "block_listing", "publish_allowed": False},
                "execution_queue_status": "idle",
                "blocking_items": bootstrap_status["blocking_items"],
                "product_mode": bootstrap_status["product_mode"],
            }
            self._write_execution_log(
                keyword=keyword,
                market=market,
                channel=channel,
                shop_domain=shop_domain,
                decision={},
                blocked_reason=str(result["message"]),
                platform_action="block_listing",
                success=False,
                rollback_reason=str(result["message"]),
                platform_execution_status=str(result["platform_execution_status"]),
                execution_queue_status=str(result["execution_queue_status"]),
            )
            return result
        listing_bundle = listing_service.build_listing(keyword=keyword, market=market, channel=channel)
        bridge_result = execution_bridge_layer.execute(
            decision=listing_bundle["decision"],
            listing_bundle=listing_bundle,
            publish_payload={"channel": channel, "shop_domain": shop_domain},
        )
        execution_adapter = client_manager.get_execution_client(channel=channel)
        oauth_session = execution_adapter.build_oauth_session(shop_domain=shop_domain)
        if oauth_code:
            oauth_session = execution_adapter.exchange_oauth_code(shop_domain=shop_domain, code=oauth_code)
        if not bridge_result["execution_bridge_mapping"]["publish_allowed"] or not listing_bundle["decision"].get("execution_allowed"):
            result = {
                "oauth": oauth_session.model_dump(mode="json"),
                "listing": listing_bundle["listing"],
                "publish": None,
                "shopify_product_id": None,
                "message": listing_bundle["decision"].get("execution_block_reason") or "执行桥接层禁止直接发布。",
                "platform_execution_status": bridge_result["platform_execution_status"],
                "execution_bridge_mapping": bridge_result["execution_bridge_mapping"],
                "execution_queue_status": bridge_result.get("execution_queue_status", "idle"),
            }
            feedback = execution_bridge_layer.on_platform_result({
                "decision_id": f"publish:{market}:{keyword}",
                "keyword": keyword,
                "market": market,
                "status": "failed",
                "listing_result": result["platform_execution_status"],
                "conversion_rate": 0.0,
                "profit_actual": 0.0,
                "profit_predicted": float(listing_bundle["decision"].get("real_profit_estimate") or 0.0),
                "platform_performance": {"channel": channel, "reason": result["message"]},
            })
            result["feedback_signal"] = feedback["feedback_signal"]
            self._write_execution_log(
                keyword=keyword,
                market=market,
                channel=channel,
                shop_domain=shop_domain,
                decision=listing_bundle["decision"],
                blocked_reason=str(result["message"]),
                platform_action=str(bridge_result.get("platform_action") or "log_only"),
                success=False,
                rollback_reason=str(result["message"]),
                platform_execution_status=str(result["platform_execution_status"]),
                execution_queue_status=str(result["execution_queue_status"]),
            )
            return result
        if not oauth_session.connected:
            result = {
                "oauth": oauth_session.model_dump(mode="json"),
                "listing": listing_bundle["listing"],
                "publish": None,
                "shopify_product_id": None,
                "message": "当前还没有完成 OAuth，先返回 mock 授权链接。",
                "platform_execution_status": bridge_result["platform_execution_status"],
                "execution_bridge_mapping": bridge_result["execution_bridge_mapping"],
                "execution_queue_status": bridge_result.get("execution_queue_status", "idle"),
            }
            self._write_execution_log(
                keyword=keyword,
                market=market,
                channel=channel,
                shop_domain=shop_domain,
                decision=listing_bundle["decision"],
                blocked_reason="等待 Shopify OAuth 授权完成",
                platform_action=str(bridge_result.get("platform_action") or "oauth_wait"),
                success=False,
                rollback_reason="当前未完成 OAuth 授权",
                platform_execution_status=str(result["platform_execution_status"]),
                execution_queue_status=str(result["execution_queue_status"]),
            )
            return result
        receipt = execution_adapter.publish_listing(
            shop_domain=shop_domain,
            listing=__import__("app.core.contracts", fromlist=["ListingDraft"]).ListingDraft.model_validate(listing_bundle["listing"]),
        )
        result = {
            "oauth": oauth_session.model_dump(mode="json"),
            "listing": listing_bundle["listing"],
            "publish": receipt.model_dump(mode="json"),
            "shopify_product_id": receipt.listing_id if channel == "shopify" else None,
            "message": "当前为 mock 发布结果，接口结构已经预留完成。",
            "platform_execution_status": bridge_result["platform_execution_status"],
            "execution_bridge_mapping": bridge_result["execution_bridge_mapping"],
            "execution_queue_status": bridge_result.get("execution_queue_status", "idle"),
        }
        feedback = execution_bridge_layer.on_platform_result({
            "decision_id": f"publish:{market}:{keyword}",
            "keyword": keyword,
            "market": market,
            "status": "success",
            "listing_result": result["platform_execution_status"],
            "conversion_rate": 0.12,
            "profit_actual": float(listing_bundle["decision"].get("real_profit_estimate") or 0.0) * 0.95,
            "profit_predicted": float(listing_bundle["decision"].get("real_profit_estimate") or 0.0),
            "platform_performance": {"channel": channel, "receipt_status": receipt.status},
        })
        result["feedback_signal"] = feedback["feedback_signal"]
        self._write_execution_log(
            keyword=keyword,
            market=market,
            channel=channel,
            shop_domain=shop_domain,
            decision=listing_bundle["decision"],
            blocked_reason="",
            platform_action=str(bridge_result.get("platform_action") or "publish_listing"),
            success=True,
            rollback_reason="",
            platform_execution_status=str(result["platform_execution_status"]),
            execution_queue_status=str(result["execution_queue_status"]),
            shopify_product_id=str(result["shopify_product_id"] or ""),
            publish_receipt=receipt.model_dump(mode="json"),
        )
        audit_logger.write(
            user_id=None,
            action="publish_action",
            payload={
                "channel": channel,
                "shop_domain": shop_domain,
                "shopify_product_id": result["shopify_product_id"],
                "platform_execution_status": result["platform_execution_status"],
            },
        )
        return result


publish_service: PublishServiceBase = PublishService()
