from __future__ import annotations

from app.core.contracts import MarketInsight, TrendPoint
from app.services.market_intelligence_engine import market_intelligence_engine as market_radar_service
from app.core.platform_router import platform_router
from app.core.real_data_layer import real_data_manager
from app.core.data_trust_engine import data_trust_engine
from app.core.supply_intelligence_engine import SupplyQuery, supply_intelligence_engine
from app.core.database import SessionLocal


class AnalysisOrchestrator:
    def build_market_context(self, *, keyword: str, market: str) -> dict:
        normalized_region = "global" if str(market or "").strip().lower() in {"shopify", "amazon", "shopee", "tiktok"} else (market or "global")
        db = SessionLocal()
        try:
            market_result = market_radar_service.analyze_keyword(
                db,
                keyword,
                region=normalized_region,
                category=None,
            )
        finally:
            db.close()
        market_insight = MarketInsight(
            source="market_real_radar",
            keyword=keyword,
            market=market,
            trend_direction=str(market_result.get("trend_direction") or "flat"),
            demand_score=int(round(float(market_result.get("demand_score") or 0))),
            competition_score=int(round(float(market_result.get("competition_score") or 0))),
            trend_points=[
                TrendPoint(
                    date=str(item.get("date") or ""),
                    score=int(round(float(item.get("score") or 0))),
                )
                for item in (market_result.get("trend_points") or [])
            ] or [
                TrendPoint(date="trend-current", score=int(round(float(market_result.get("trend_strength") or 0)))),
            ],
            summary="；".join([
                str((market_result.get("reasoning") or {}).get("demand_reason") or ""),
                str((market_result.get("reasoning") or {}).get("competition_reason") or ""),
                str((market_result.get("reasoning") or {}).get("trend_reason") or ""),
                f"市场机会 {((market_result.get('market_opportunity') or {}).get('entry_recommendation') or '')}，机会分 {((market_result.get('market_opportunity') or {}).get('market_score') or 0)}。",
            ]),
            market_score=float(market_result.get("market_score") or 0),
            recommendation=str(market_result.get("recommendation") or "WATCH"),
            confidence=float(market_result.get("confidence") or 0),
            risk_flags=list(market_result.get("risk_flags") or []),
            platform_signals=dict(market_result.get("platform_signals") or {}),
            keyword_cluster=dict(market_result.get("keyword_cluster") or {}),
            platform_compatibility=dict(market_result.get("platform_compatibility") or {}),
            is_mock=bool(market_result.get("is_mock")),
            mock_penalty_applied=bool(market_result.get("mock_ratio", 0) > 0),
        )
        return {
            "market_intelligence": market_result,
            "market_insight": market_insight,
            "analysis_context": {
                "market_context": market_result,
                "market_intelligence": market_result,
                "trusted_market_data": {
                    "market_score": market_result.get("market_score"),
                    "market_opportunity": market_result.get("market_opportunity"),
                    "confidence": market_result.get("confidence"),
                    "source_status": market_result.get("source_status"),
                    "all_sources_mock": bool(market_result.get("real_ratio", 0) == 0 and market_result.get("partial_ratio", 0) == 0),
                    "demand_score": market_result.get("demand_score"),
                    "trend_strength": market_result.get("trend_strength"),
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
