from __future__ import annotations

from sqlalchemy.orm import Session

from app.adapters.shopify.shopify_product_draft_service import shopify_product_draft_service
from app.core.analysis_orchestrator import analysis_orchestrator
from app.core.business_feedback_engine import business_feedback_engine
from app.core.business_opportunity_v3 import (
    AmazonSignalBlock,
    BusinessOpportunityV3,
    ExecutionSignalBlock,
    MarketSignalBlock,
    ProfitSignalBlock,
    SupplierSignalBlock,
)
from app.core.execution_bridge_layer import execution_bridge_layer
from app.core.execution_control_layer import execution_control_layer
from app.core.execution_queue import execution_queue
from app.core.opportunity_scoring_engine import opportunity_scoring_engine
from app.repositories.business_opportunity_history import business_opportunity_history_repository
from app.services.profit_truth_engine import profit_truth_engine


class BusinessOpportunityV3Service:
    def analyze(self, db: Session, *, keyword: str, market: str) -> BusinessOpportunityV3:
        context = analysis_orchestrator.build_analysis_context(keyword=keyword, market=market)
        market_intelligence = context.get("market_intelligence") or {}
        amazon_signal = ((market_intelligence.get("platform_signals") or {}).get("amazon")) or {}
        supply_intelligence = context.get("supply_intelligence") or {}
        cost_estimate = supply_intelligence.get("cost_estimate") or {}
        selected_supplier = supply_intelligence.get("selected_supplier") or {}
        market_score = float(market_intelligence.get("market_score") or 0)
        supplier_score = float(supply_intelligence.get("supplier_score") or 0)
        competition_score = float(amazon_signal.get("competition_density") or market_intelligence.get("competition_score") or 0)
        expected_price = float(
            (supply_intelligence.get("profit_preview") or {}).get("suggested_price")
            or cost_estimate.get("suggested_price")
            or 0
        )
        if expected_price <= 0:
            expected_price = float(cost_estimate.get("target_price") or 0)
        if expected_price <= 0:
            expected_price = round(
                max(
                    39.9,
                    float(cost_estimate.get("landed_cost") or 0) * 2.2,
                ),
                2,
            )
        real_profit = profit_truth_engine.calculate_from_supply_intelligence(
            supply_intelligence=supply_intelligence,
            cost_estimate=cost_estimate,
            selling_price=expected_price,
            ad_cost=float(cost_estimate.get("marketing_cost") or 0),
            currency_loss=0,
        )
        profit_score = float(real_profit.get("real_profit_margin") or 0)
        if profit_score <= 1:
            profit_score *= 100
        opportunity_result = opportunity_scoring_engine.score(
            market_score=market_score,
            supplier_score=supplier_score,
            profit_score=profit_score,
            competition_score=competition_score,
        )
        decision_label = str(opportunity_result["recommendation"])
        trust_level = round(
            (
                float(market_intelligence.get("confidence") or 0)
                + float(supply_intelligence.get("supplier_confidence") or 0)
                + float(real_profit.get("confidence") or 0)
            ) / 3,
            4,
        )
        execution_policy = execution_control_layer.build_execution_policy(
            trust_level=trust_level,
            is_mock=bool(market_intelligence.get("is_mock")) or bool(supply_intelligence.get("is_mock")),
            risk_level="medium",
        )
        draft_allowed = decision_label == "TEST" and float(real_profit.get("confidence") or 0) >= 0.55
        publish_allowed = "SCALE" in list(execution_policy["allowed_actions"] or [])
        shopify_ready = bool((context.get("platform_data") or {}).get("shopify_real_products"))

        result = BusinessOpportunityV3(
            keyword=keyword,
            market=market,
            market_signal=MarketSignalBlock(
                demand_score=float(market_intelligence.get("demand_score") or 0),
                trend_direction=str(market_intelligence.get("trend_direction") or "flat"),
                competition_level=str(market_intelligence.get("competition_level") or "medium"),
                confidence=float(market_intelligence.get("confidence") or 0),
            ),
            amazon_signal=AmazonSignalBlock(
                demand_score=float(amazon_signal.get("demand_score") or 0),
                review_density=float(amazon_signal.get("review_count") or 0),
                competition_density=float(amazon_signal.get("competition_density") or 0),
                price_range=dict(amazon_signal.get("price_range") or {}),
            ),
            supplier_signal=SupplierSignalBlock(
                supplier_score=supplier_score,
                supplier_source=str(supply_intelligence.get("data_source") or "unavailable"),
                product_cost=float(cost_estimate.get("product_cost") or 0),
                MOQ=int(selected_supplier.get("min_order_quantity") or 0),
                supplier_confidence=float(supply_intelligence.get("supplier_confidence") or 0),
            ),
            profit_signal=ProfitSignalBlock(
                cost=float(cost_estimate.get("product_cost") or 0),
                shipping_cost=float(cost_estimate.get("shipping_estimate") or 0),
                platform_fee=float(cost_estimate.get("platform_fee") or 0),
                ad_cost=float(cost_estimate.get("marketing_cost") or 0),
                expected_price=expected_price,
                gross_margin=float(real_profit.get("gross_profit") or 0),
                net_margin=round(profit_score, 2),
                profit_confidence=float(real_profit.get("confidence") or 0),
            ),
            decision=decision_label,
            execution=ExecutionSignalBlock(
                shopify_ready=shopify_ready,
                draft_allowed=draft_allowed,
                publish_allowed=publish_allowed,
            ),
            market_score=round(market_score, 2),
            supplier_score=round(supplier_score, 2),
            profit_margin=round(profit_score, 2),
            opportunity_score=float(opportunity_result["score"]),
            confidence=trust_level,
            risk_flags=list(opportunity_result.get("risk_flags", [])),
            source_status=dict(market_intelligence.get("source_status") or {}),
            shopify_action="draft_allowed" if draft_allowed else "blocked",
        )
        history = business_opportunity_history_repository.create(
            db,
            keyword=keyword,
            market=market,
            market_score=result.market_score,
            supplier_score=result.supplier_score,
            profit_margin=result.profit_margin,
            opportunity_score=result.opportunity_score,
            decision=result.decision,
            execution_result="analyzed",
            shopify_action=result.shopify_action,
            actual_result={},
            snapshot=result.model_dump(mode="json"),
            note="analysis_created",
        )
        result.history_id = history.id
        return result

    def execute(
        self,
        db: Session,
        *,
        keyword: str,
        market: str,
        shop_domain: str,
    ) -> dict:
        analyzed = self.analyze(db, keyword=keyword, market=market)
        action_level = "WATCH"
        if analyzed.decision == "TEST":
            action_level = "TEST"
        elif analyzed.decision == "BUY":
            action_level = "SCALE"
        elif analyzed.decision == "IGNORE":
            action_level = "WATCH"
        decision_payload = {
            "keyword": keyword,
            "market": market,
            "action_level": action_level,
            "execution_allowed": action_level in {"TEST", "SCALE", "AUTO_LIST"},
            "execution_block_reason": "" if action_level in {"TEST", "SCALE", "AUTO_LIST"} else "当前机会只允许观察，不允许执行。",
            "recommended_price": analyzed.profit_signal.expected_price,
            "real_profit_estimate": analyzed.profit_signal.gross_margin,
        }
        execution = execution_bridge_layer.execute(decision=decision_payload, listing_bundle=None, publish_payload={"channel": "shopify", "shop_domain": shop_domain})
        draft_result: dict = {}
        if action_level == "TEST":
            listing = self._build_listing_payload(keyword=keyword, analyzed=analyzed)
            draft_result = shopify_product_draft_service.create_draft(
                shop_domain=shop_domain,
                listing=listing,
                supplier_reference=str(analyzed.supplier_signal.supplier_source),
                cost=float(analyzed.profit_signal.cost),
                margin=float(analyzed.profit_signal.net_margin),
            )
            execution["platform_execution_status"] = draft_result.get("status") or execution["platform_execution_status"]
            execution["platform_action"] = "create_shopify_draft"
            execution["success"] = bool(draft_result.get("is_real")) and draft_result.get("status") == "draft_created"
            if draft_result.get("error"):
                execution["rollback_reason"] = str(draft_result.get("detail") or draft_result.get("error"))
        elif action_level == "SCALE":
            execution_queue.queue_batch({"keyword": keyword, "market": market, "decision": decision_payload})
            execution["platform_execution_status"] = "queued_batch"
            execution["execution_queue_status"] = "queue_batch"
        feedback = business_feedback_engine.record_feedback(
            db,
            history_id=analyzed.history_id,
            keyword=keyword,
            market=market,
            shop_domain=shop_domain,
            listing_result=str(execution.get("platform_execution_status") or "blocked"),
            predicted_profit=float(analyzed.profit_signal.gross_margin or 0),
            platform_performance={"shopify_action": execution.get("platform_action"), "draft_result": draft_result},
        )
        business_opportunity_history_repository.update_actual_result(
            db,
            record_id=int(analyzed.history_id or 0),
            actual_result={"execution": execution, "draft": draft_result, "feedback": feedback},
            execution_result=str(execution.get("platform_execution_status") or "blocked"),
            note="execute_called",
        )
        return {
            "keyword": keyword,
            "market": market,
            "recommendation": analyzed.decision,
            "shopify_action": execution.get("platform_action") or "blocked",
            "execution": execution,
            "draft": draft_result,
            "feedback": feedback,
            "history_id": analyzed.history_id,
        }

    def history(self, db: Session, *, limit: int = 50) -> list[dict]:
        records = business_opportunity_history_repository.list_recent(db, limit=limit)
        return [
            {
                "id": item.id,
                "keyword": item.keyword,
                "market": item.market,
                "market_score": item.market_score,
                "supplier_score": item.supplier_score,
                "profit_margin": item.profit_margin,
                "opportunity_score": item.opportunity_score,
                "decision": item.decision,
                "execution_result": item.execution_result,
                "shopify_action": item.shopify_action,
                "actual_result": item.actual_result,
                "created_at": item.created_at.isoformat() if item.created_at else "",
            }
            for item in records
        ]

    def _build_listing_payload(self, *, keyword: str, analyzed: BusinessOpportunityV3) -> dict:
        return {
            "channel": "shopify",
            "product_title": keyword,
            "seo_title": f"{keyword.title()} | Shopify Draft",
            "listing_title": f"{keyword.title()} | Shopify Draft",
            "listing_description": f"{keyword} 当前进入 TEST，先创建 Shopify Draft 做验证。",
            "description": f"{keyword} 当前进入 TEST，先创建 Shopify Draft 做验证。",
            "keywords": [keyword, analyzed.market, "shopify"],
            "bullet_points": ["先做 Draft", "不直接发布", "先看利润再看反馈"],
            "image_structure": ["主图", "卖点图", "细节图"],
            "selling_points": ["市场已验证", "供应已匹配", "利润已计算"],
            "tags": [keyword, analyzed.market, "draft", "shanghang-ai"],
            "price_suggestion": analyzed.profit_signal.expected_price,
            "suggested_price": analyzed.profit_signal.expected_price,
        }


business_opportunity_v3_service = BusinessOpportunityV3Service()
