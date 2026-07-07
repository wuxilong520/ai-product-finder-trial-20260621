from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.execution_bridge_layer import execution_bridge_layer
from app.core.ai_engine import ai_engine
from app.core.contracts import ListingDraft
from app.services.decision_service import decision_service
from app.services.analyze_service import analyze_service
from app.core.production_bootstrap_layer import production_bootstrap_layer


class ListingServiceBase(ABC):
    @abstractmethod
    def build_listing(self, *, keyword: str, market: str, channel: str) -> dict:
        raise NotImplementedError


class ListingService(ListingServiceBase):
    def build_listing(self, *, keyword: str, market: str, channel: str) -> dict:
        analysis = analyze_service.analyze(keyword=keyword, market=market)
        decision = decision_service.decide(
            keyword=keyword,
            market=market,
            profit=analysis.profit_breakdown,
            analysis_context={
                "keyword": keyword,
                "market": market,
                "market_summary": analysis.market_insight.summary,
                "suggested_price": analysis.profit_breakdown.estimated_sell_price,
                "estimated_profit": analysis.profit_breakdown.estimated_profit,
                "estimated_margin_rate": analysis.profit_breakdown.estimated_margin_rate,
            },
            data_trust=analysis.trust_report,
        )
        ai_result = ai_engine.complete_json(
            task_name="listing",
            system_prompt="你是商航AI的上架文案引擎，只返回结构化 JSON。",
            user_prompt=f"为 {keyword} 生成 {channel} 上架文案。",
            context={
                "keyword": keyword,
                "market": market,
                "channel": channel,
                "decision": decision.model_dump(mode="json"),
            },
        )
        draft = ListingDraft(
            channel=channel,
            product_title=analysis.selected_offer.product_title,
            seo_title=str(ai_result["seo_title"]),
            listing_title=str(ai_result["listing_title"]),
            listing_description=str(ai_result["listing_description"]),
            description=str(ai_result["description"]),
            keywords=list(ai_result["keywords"]),
            bullet_points=list(ai_result["bullet_points"]),
            image_structure=list(ai_result["image_structure"]),
            selling_points=list(ai_result["selling_points"]),
            tags=list(ai_result["tags"]),
            price_suggestion=decision.recommended_price,
            suggested_price=decision.recommended_price,
        )
        listing_payload = {
            "analysis": analysis.model_dump(mode="json"),
            "decision": decision.model_dump(mode="json"),
            "listing": draft.model_dump(mode="json"),
        }
        bridge_result = execution_bridge_layer.execute(
            decision=decision.model_dump(mode="json"),
            listing_bundle=listing_payload,
            publish_payload={"channel": channel},
        )
        decision_payload = {
            **decision.model_dump(mode="json"),
            "execution_bridge_mapping": bridge_result["execution_bridge_mapping"],
            "platform_execution_status": bridge_result["platform_execution_status"],
            "execution_queue_status": bridge_result.get("execution_queue_status", "idle"),
        }
        bootstrap_status = production_bootstrap_layer.status()
        platform_data = (analysis.trust_report or {}).get('platform_data', {})
        data_trust_score = (analysis.trust_report or {}).get('data_trust_score', 0.0)
        return {
            "analysis": analysis.model_dump(mode="json"),
            "decision": decision_payload,
            "listing": draft.model_dump(mode="json"),
            "execution": bridge_result,
            "production_bootstrap_status": bootstrap_status,
            "shopify_candidates": platform_data.get('shopify_candidates', []),
            "alibaba_suppliers": platform_data.get('alibaba_suppliers', []),
            "shopify_real_products": platform_data.get('shopify_real_products', []),
            "1688_real_suppliers": platform_data.get('1688_real_suppliers', []),
            "cost_estimate": analysis.profit_breakdown.cost_estimate,
            "profit_margin": analysis.profit_breakdown.profit_margin,
            "data_trust_score": data_trust_score,
            "profit_truth_score": analysis.profit_breakdown.profit_truth_score,
            "execution_recommendation": 'observe' if data_trust_score < 0.6 else ('shopify_draft' if decision_payload.get('action_level') == 'TEST' else 'observe'),
            "platform_recommendation": 'shopify' if decision_payload.get('action_level') in {'TEST', 'AUTO_LIST'} else 'observe',
            "execution_target_platform": bridge_result.get('execution_target_platform', 'none'),
            "publish_decision": (bridge_result.get('platform_action_result') or {}).get('publish_decision', 'no_publish'),
        }


listing_service: ListingServiceBase = ListingService()
