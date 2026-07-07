from __future__ import annotations

from app.core.contracts import MarketInsight, TrendPoint
from app.core.market_intelligence_engine import MarketInsight as EngineMarketInsight, MarketQuery, market_intelligence_engine
from app.core.platform_router import platform_router
from app.core.real_data_layer import real_data_manager
from app.core.data_trust_engine import data_trust_engine


class AnalysisOrchestrator:
    def build_market_context(self, *, keyword: str, market: str) -> dict:
        market_result = market_intelligence_engine.analyze(
            MarketQuery(
                keyword=keyword,
                region=market or "global",
            )
        )
        market_intelligence = market_result.market_intelligence
        market_insight = MarketInsight(
            source="market_intelligence_engine",
            keyword=keyword,
            market=market,
            trend_direction="up" if market_intelligence.trend_strength >= 55 else "flat",
            demand_score=int(round(market_intelligence.demand_score)),
            competition_score=int(round(market_intelligence.market_saturation)),
            trend_points=[
                TrendPoint(date="2026-06-01", score=max(0, int(round(market_intelligence.trend_strength - 12)))),
                TrendPoint(date="2026-06-08", score=max(0, int(round(market_intelligence.trend_strength - 8)))),
                TrendPoint(date="2026-06-15", score=max(0, int(round(market_intelligence.trend_strength - 4)))),
                TrendPoint(date="2026-06-22", score=max(0, int(round(market_intelligence.trend_strength - 2)))),
                TrendPoint(date="2026-06-29", score=int(round(market_intelligence.trend_strength))),
            ],
            summary="；".join([
                market_result.reasoning["demand_reason"],
                market_result.reasoning["competition_reason"],
                market_result.reasoning["trend_reason"],
            ]),
            market_score=market_result.market_score,
            recommendation=market_result.recommendation,
            confidence=market_result.confidence,
            risk_flags=market_result.risk_flags,
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
                "market_intelligence": market_result.model_dump(mode="json"),
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

    def build_analysis_context(self, *, keyword: str, market: str) -> dict:
        market_context = self.build_market_context(keyword=keyword, market=market)
        platform_context = self.build_platform_context(keyword=keyword)
        return {
            **market_context,
            **platform_context,
            "analysis_context": {
                **market_context["analysis_context"],
                "platform_data": platform_context["platform_data"],
            },
        }


analysis_orchestrator = AnalysisOrchestrator()
