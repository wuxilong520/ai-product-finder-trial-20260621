from __future__ import annotations

from app.core.contracts import MarketInsight, TrendPoint
from app.core.market_signal_engine import market_signal_engine
from app.core.market_opportunity_model import market_opportunity_model
from app.core.market_intelligence_engine import MarketInsight as EngineMarketInsight, MarketQuery, market_intelligence_engine
from app.core.platform_router import platform_router
from app.core.real_data_layer import real_data_manager
from app.core.data_trust_engine import data_trust_engine
from app.core.supply_intelligence_engine import SupplyQuery, supply_intelligence_engine
from app.core.database import SessionLocal


class AnalysisOrchestrator:
    def build_market_context(self, *, keyword: str, market: str) -> dict:
        normalized_region = "global" if str(market or "").strip().lower() in {"shopify", "amazon", "shopee", "tiktok"} else (market or "global")
        market_result = market_intelligence_engine.analyze(
            MarketQuery(
                keyword=keyword,
                region=normalized_region,
            )
        )
        market_intelligence = market_result.market_intelligence
        signal_bundle = market_signal_engine.build(
            keyword=keyword,
            region=normalized_region,
            data_sources=market_intelligence.data_sources,
            market_intelligence=market_intelligence.model_dump(mode="json"),
        )
        market_opportunity = market_opportunity_model.evaluate(
            demand_score=signal_bundle["demand_score"],
            trend_score=signal_bundle["trend_score"],
            competition_score=signal_bundle["competition_score"],
            platform_compatibility=market_intelligence.platform_compatibility.model_dump(mode="json"),
        )
        market_intelligence = market_intelligence.model_copy(update={
            "market_signals": signal_bundle["market_signals"],
            "market_growth": signal_bundle["market_growth"],
            "trend_direction": signal_bundle["trend_direction"],
            "market_opportunity": market_opportunity.model_dump(mode="json"),
            "source_status": signal_bundle["source_status"],
            "confidence": min(float(signal_bundle["confidence"]), 0.3) if signal_bundle["all_mock"] else float(signal_bundle["confidence"]),
            "all_sources_mock": signal_bundle["all_mock"],
        })
        market_insight = MarketInsight(
            source="market_intelligence_engine",
            keyword=keyword,
            market=market,
            trend_direction=market_intelligence.trend_direction,
            demand_score=int(round(signal_bundle["demand_score"])),
            competition_score=int(round(signal_bundle["competition_score"])),
            trend_points=[
                TrendPoint(
                    date=str(item.get("date") or ""),
                    score=int(round(float(item.get("score") or 0))),
                )
                for item in (market_intelligence.trend_points or [])
            ] or [
                TrendPoint(date="trend-current", score=int(round(market_intelligence.trend_strength))),
            ],
            summary="；".join([
                market_result.reasoning["demand_reason"],
                market_result.reasoning["competition_reason"],
                market_result.reasoning["trend_reason"],
                f"市场机会 {market_opportunity.level}，机会分 {market_opportunity.score}。",
            ]),
            market_score=market_result.market_score,
            recommendation=market_opportunity.recommendation,
            confidence=market_intelligence.confidence,
            risk_flags=sorted(set([*market_result.risk_flags, "all_sources_mock"])) if signal_bundle["all_mock"] else market_result.risk_flags,
            platform_signals=market_intelligence.platform_signals.model_dump(mode="json"),
            keyword_cluster=market_intelligence.keyword_cluster.model_dump(mode="json"),
            platform_compatibility=market_intelligence.platform_compatibility.model_dump(mode="json"),
            is_mock=market_intelligence.is_mock,
            mock_penalty_applied=market_intelligence.mock_penalty > 0,
        )
        return {
            "market_intelligence": market_result.model_dump(mode="json"),
            "market_insight": market_insight,
            "analysis_context": {
                "market_intelligence": {
                    **market_result.model_dump(mode="json"),
                    "market_signals": market_intelligence.market_signals,
                    "market_growth": market_intelligence.market_growth,
                    "market_opportunity": market_intelligence.market_opportunity,
                    "source_status": market_intelligence.source_status,
                    "trend_direction": market_intelligence.trend_direction,
                    "confidence": market_intelligence.confidence,
                    "all_sources_mock": market_intelligence.all_sources_mock,
                },
                "trusted_market_data": {
                    "market_score": market_result.market_score,
                    "market_opportunity": market_intelligence.market_opportunity,
                    "confidence": market_intelligence.confidence,
                    "source_status": market_intelligence.source_status,
                    "all_sources_mock": market_intelligence.all_sources_mock,
                },
            },
        }

    def build_platform_context(self, *, keyword: str) -> dict:
        shopify_candidates = [platform_router.normalize_product_data(item) for item in platform_router.get_shopify_candidates(keyword)]
        alibaba_suppliers = [platform_router.normalize_product_data(item) for item in platform_router.get_alibaba_suppliers(keyword)]
        shopify_state = real_data_manager.detect_state(shopify_candidates)
        alibaba_state = real_data_manager.detect_state(alibaba_suppliers)
        shopify_real_products = [item for item in shopify_candidates if item.get('data_source_type') == 'real']
        alibaba_real_suppliers = [item for item in alibaba_suppliers if item.get('data_source_type') == 'real']
        combined_source_type = 'real' if shopify_state['data_source_type'] == 'real' and alibaba_state['data_source_type'] == 'real' else 'partial' if 'partial' in {shopify_state['data_source_type'], alibaba_state['data_source_type']} or 'real' in {shopify_state['data_source_type'], alibaba_state['data_source_type']} else 'mock'
        data_trust_score = data_trust_engine.score(data_source_type=combined_source_type, inconsistent=False)
        return {
            'shopify_data_source': 'shopify_platform',
            '1688_data_source': 'alibaba_1688_platform',
            'data_source_type': combined_source_type,
            'data_trust_score': data_trust_score,
            'platform_data': {
                'shopify_candidates': shopify_candidates,
                'alibaba_suppliers': alibaba_suppliers,
                'shopify_real_products': shopify_real_products,
                '1688_real_suppliers': alibaba_real_suppliers,
            },
        }

    def build_supply_context(self, *, keyword: str, market: str, market_context: dict) -> dict:
        market_intelligence = (market_context.get("market_intelligence") or {}).get("market_intelligence") or {}
        expected_price = None
        try:
            shopify_signal = float(((market_intelligence.get("platform_signals") or {}).get("shopify_category_activity")) or 0)
            expected_price = round(max(39.9, 0.8 * shopify_signal + 39.9), 2)
        except Exception:
            expected_price = None
        db = SessionLocal()
        try:
            supply_result = supply_intelligence_engine.analyze(
                db,
                SupplyQuery(
                    keyword=keyword,
                    category=None,
                    target_market=market or "global",
                    expected_price=expected_price,
                    quantity=100,
                ),
            )
        finally:
            db.close()
        return {
            "supply_intelligence": supply_result,
            "supply_context": {
                "suppliers": supply_result.get("suppliers", []),
                "selected_supplier": supply_result.get("selected_supplier"),
                "supplier_score": supply_result.get("supplier_score", 0),
                "supplier_quality": supply_result.get("supplier_quality", "not_recommended"),
                "supplier_confidence": supply_result.get("supplier_confidence", 0),
                "risk_flags": supply_result.get("supplier_risk", supply_result.get("risk_flags", [])),
                "confidence": supply_result.get("confidence", 0),
                "is_mock": supply_result.get("is_mock", True),
                "procurement_recommendation": supply_result.get("procurement_recommendation", {}),
            },
            "cost_context": supply_result.get("cost_estimate", {}),
        }

    def build_analysis_context(self, *, keyword: str, market: str) -> dict:
        market_context = self.build_market_context(keyword=keyword, market=market)
        platform_context = self.build_platform_context(keyword=keyword)
        supply_context = self.build_supply_context(keyword=keyword, market=market, market_context=market_context)
        return {
            **market_context,
            **platform_context,
            **supply_context,
            "analysis_context": {
                **market_context["analysis_context"],
                "platform_data": platform_context["platform_data"],
                "supply_context": supply_context["supply_context"],
                "cost_context": supply_context["cost_context"],
            },
        }


analysis_orchestrator = AnalysisOrchestrator()
