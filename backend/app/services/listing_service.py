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
    def _normalize_text(self, ai_result: dict, primary_key: str, fallback: str) -> str:
        value = ai_result.get(primary_key)
        if value is None:
            if primary_key == "seo_title":
                value = ai_result.get("listing_title")
            elif primary_key == "listing_title":
                value = ai_result.get("seo_title")
            elif primary_key == "listing_description":
                value = ai_result.get("description")
            elif primary_key == "description":
                value = ai_result.get("listing_description")
        if value is None:
            value = fallback
        return str(value)

    def _normalize_list(self, ai_result: dict, key: str, fallback: list[str]) -> list[str]:
        value = ai_result.get(key)
        if isinstance(value, list) and value:
            return [str(item) for item in value if str(item).strip()]
        return fallback

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
        default_title = f"{keyword.title()} | 商航AI推荐上架"
        default_description = f"围绕 {keyword} 生成的基础上架文案，当前可用于最小验证。"
        draft = ListingDraft(
            channel=channel,
            product_title=analysis.selected_offer.product_title,
            seo_title=self._normalize_text(ai_result, "seo_title", default_title),
            listing_title=self._normalize_text(ai_result, "listing_title", default_title),
            listing_description=self._normalize_text(ai_result, "listing_description", default_description),
            description=self._normalize_text(ai_result, "description", default_description),
            keywords=self._normalize_list(ai_result, "keywords", [keyword, market, channel]),
            bullet_points=self._normalize_list(
                ai_result,
                "bullet_points",
                [
                    "先做小单验证，再看是否放量",
                    "当前利润测算已完成基础校验",
                    "建议结合供应稳定性再决定是否正式上架",
                ],
            ),
            image_structure=self._normalize_list(
                ai_result,
                "image_structure",
                ["主图", "场景图", "细节图"],
            ),
            selling_points=self._normalize_list(
                ai_result,
                "selling_points",
                ["标题围绕需求词生成", "保留基础利润空间", "支持后续接真实平台发布"],
            ),
            tags=self._normalize_list(ai_result, "tags", [keyword, market, channel, "shanghang-ai"]),
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
