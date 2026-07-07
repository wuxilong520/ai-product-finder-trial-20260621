from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.analysis_engine import analysis_engine
from app.core.contracts import AnalyzeBundle, SupplyOffer
from app.core.data_trust_layer import data_trust_layer
from app.integration.client_manager import client_manager
from app.core.analysis_orchestrator import analysis_orchestrator
from app.services.explain_engine import explain_engine
from app.services.profit_engine import profit_engine
from app.services.trace_engine import trace_engine
from app.core.feedback_loop_v2 import feedback_loop_v2


class AnalyzeServiceBase(ABC):
    @abstractmethod
    def analyze(self, *, keyword: str, market: str, plan_name: str = "free") -> AnalyzeBundle:
        raise NotImplementedError


class AnalyzeService(AnalyzeServiceBase):
    def analyze(self, *, keyword: str, market: str, plan_name: str = "free") -> AnalyzeBundle:
        trace = trace_engine.start(keyword=keyword, market=market)
        route = client_manager.resolve_route(market=market, channel="shopify")
        orchestrated_context = analysis_orchestrator.build_analysis_context(keyword=keyword, market=market)
        market_insight = orchestrated_context["market_insight"]
        market_trust = data_trust_layer.evaluate(
            data=market_insight.model_dump(mode="json"),
            source_type=self._infer_source_type(market_insight.source),
            freshness_score=self._freshness_from_source(market_insight.source),
            confidence_score=self._confidence_from_market(market_insight.demand_score, market_insight.competition_score),
        )
        trace_engine.append(
            trace=trace,
            step="market_analysis",
            adapter="market_intelligence_engine",
            message="已完成市场趋势分析",
            payload=market_insight.model_dump(mode="json"),
        )
        trace_engine.append(
            trace=trace,
            step="market_data_trust",
            adapter="data_trust_layer",
            message="已完成市场数据可信度标记",
            payload=market_trust.model_dump(mode="json"),
        )

        supply_adapter = route.supply_client
        supply_offers = supply_adapter.search_supply(keyword=keyword, market=market)
        selected_offer = self._select_best_offer(supply_offers)
        supply_trust = data_trust_layer.evaluate(
            data=selected_offer.model_dump(mode="json"),
            source_type=self._infer_source_type(selected_offer.source),
            freshness_score=self._freshness_from_supply(selected_offer.shipping_days),
            confidence_score=self._confidence_from_supply(selected_offer.rating, selected_offer.min_order_qty),
        )
        trace_engine.append(
            trace=trace,
            step="supply_search",
            adapter=supply_adapter.adapter_name,
            message="已完成供应链搜索",
            payload={"offer_count": len(supply_offers)},
        )
        trace_engine.append(
            trace=trace,
            step="supply_data_trust",
            adapter="data_trust_layer",
            message="已完成供应链数据可信度标记",
            payload=supply_trust.model_dump(mode="json"),
        )
        platform_context = {
            key: value for key, value in orchestrated_context.items()
            if key in {"shopify_data_source", "1688_data_source", "data_source_type", "data_trust_score", "platform_data"}
        }
        profit = profit_engine.calculate(
            market_insight=market_insight,
            supply_offer=selected_offer,
            platform_data=platform_context.get('platform_data'),
        )
        trace_engine.append(
            trace=trace,
            step="profit_preview",
            adapter="profit_engine",
            message="已完成利润测算",
            payload=profit.model_dump(mode="json"),
        )
        combined_trust = data_trust_layer.aggregate(market_trust, supply_trust)
        trace_engine.append(
            trace=trace,
            step="overall_data_trust",
            adapter="data_trust_layer",
            message="已完成整体数据可信度汇总",
            payload=combined_trust.model_dump(mode="json"),
        )

        analysis_outcome = analysis_engine.run(
            keyword=keyword,
            market_data=market_insight,
            supply_data=supply_offers,
            cost_data=profit,
            trend_data=[point.model_dump(mode="json") for point in market_insight.trend_points],
            competition_data={"competition_score": market_insight.competition_score},
            plan_name=plan_name,
        )
        adjusted_score = self._adjust_score_by_trust(analysis_outcome.score, combined_trust.trust_level)
        latest_feedback = feedback_loop_v2.latest_signal(keyword=keyword, market=market)
        adjusted_score, ai_adjustment_suggestion = self._adjust_score_by_feedback(
            adjusted_score=adjusted_score,
            latest_feedback=latest_feedback,
        )
        analysis_outcome = analysis_outcome.model_copy(
            update={
                "score": adjusted_score,
                "trust_adjusted_score": adjusted_score,
                "fallback_marked": combined_trust.fallback_marked,
                "trace": [
                    *analysis_outcome.trace,
                    f"trust_level:{combined_trust.trust_level}",
                    "fallback_marked" if combined_trust.fallback_marked else "trust_ok",
                    f"feedback_adjustment:{ai_adjustment_suggestion.get('score_adjustment', 0)}",
                ],
            }
        )
        trace_engine.append(
            trace=trace,
            step="analysis_engine",
            adapter="analysis_engine",
            message="已完成统一分析引擎判断",
            payload=analysis_outcome.model_dump(mode="json"),
        )

        explain = explain_engine.build(
            decision=self._build_pre_decision(
                keyword=keyword,
                market=market,
                profit=profit,
                analysis_outcome=analysis_outcome,
            ),
            profit=profit,
        )
        trace_engine.append(
            trace=trace,
            step="explain_preview",
            adapter="explain_engine",
            message="已完成解释信息整理",
            payload=explain.model_dump(mode="json"),
        )

        return AnalyzeBundle(
            market_insight=market_insight,
            supply_offers=supply_offers,
            selected_offer=selected_offer,
            profit_breakdown=profit,
            analysis_outcome=analysis_outcome,
            trust_report={
                "market": market_trust.model_dump(mode="json"),
                "supply": supply_trust.model_dump(mode="json"),
                "overall": combined_trust.model_dump(mode="json"),
            },
            trace=trace,
            explain=explain.model_copy(update={
                'next_actions': [*explain.next_actions, '已接入 Shopify + 1688 平台候选数据'],
            }),
        ).model_copy(update={
            'trust_report': {
                **{
                    "market": market_trust.model_dump(mode="json"),
                    "supply": supply_trust.model_dump(mode="json"),
                    "overall": combined_trust.model_dump(mode="json"),
                },
                "market_intelligence": orchestrated_context.get("market_intelligence", {}),
                **platform_context,
            }
        })

    def _select_best_offer(self, offers: list[SupplyOffer]) -> SupplyOffer:
        ranked = sorted(offers, key=lambda item: (-item.rating, item.price, item.shipping_days))
        return ranked[0]

    def _build_pre_decision(self, *, keyword: str, market: str, profit, analysis_outcome) -> object:
        from app.core.contracts import DecisionRecord

        verdict = "go" if analysis_outcome.recommend else "watch"
        risk_level = str(analysis_outcome.risk)
        return DecisionRecord(
            keyword=keyword,
            market=market,
            verdict=verdict,
            confidence_score=analysis_outcome.score,
            recommended_price=profit.estimated_sell_price,
            risk_level=risk_level,
            reasons=[
                analysis_outcome.reasoning,
                "趋势数据与供应链报价已经合并分析",
                f"下一步建议：{analysis_outcome.action}",
            ],
            decision_score=float(analysis_outcome.score),
            strategy_mode="sourcing",
            trust_adjusted_score=float(analysis_outcome.trust_adjusted_score or analysis_outcome.score),
            real_profit_estimate=float(profit.estimated_profit),
        )

    def _infer_source_type(self, source: str) -> str:
        normalized = str(source or "").lower()
        if "mock" in normalized:
            return "mock"
        if "cache" in normalized:
            return "cached"
        if "real" in normalized or "live" in normalized:
            return "real"
        return "estimated"

    def _freshness_from_source(self, source: str) -> float:
        normalized = self._infer_source_type(source)
        return {
            "real": 0.95,
            "cached": 0.75,
            "estimated": 0.6,
            "mock": 0.2,
        }[normalized]

    def _freshness_from_supply(self, shipping_days: int) -> float:
        if shipping_days <= 3:
            return 0.92
        if shipping_days <= 7:
            return 0.78
        if shipping_days <= 15:
            return 0.62
        return 0.45

    def _confidence_from_market(self, demand_score: int, competition_score: int) -> float:
        score = ((float(demand_score) * 0.65) + ((100 - float(competition_score)) * 0.35)) / 100
        return round(max(0.0, min(1.0, score)), 4)

    def _confidence_from_supply(self, rating: float, min_order_qty: int) -> float:
        rating_score = max(0.0, min(1.0, float(rating) / 5))
        moq_penalty = 0.15 if min_order_qty > 200 else 0.08 if min_order_qty > 50 else 0.0
        return round(max(0.0, min(1.0, rating_score - moq_penalty)), 4)

    def _adjust_score_by_trust(self, score: int, trust_level: float) -> int:
        if trust_level < 0.6:
            return max(0, int(round(score * 0.85)))
        return int(score)

    def _adjust_score_by_feedback(self, *, adjusted_score: int, latest_feedback: dict) -> tuple[int, dict]:
        if not latest_feedback:
            return adjusted_score, {
                "score_adjustment": 0,
                "reason": "当前还没有真实执行反馈，先不调整。",
                "trust_weight_adjustment": 0,
                "strategy_score_adjustment": 0,
                "risk_evaluation_adjustment": "none",
            }
        error_delta = abs(float(latest_feedback.get("error_delta") or 0))
        threshold = 5.0
        if error_delta > threshold:
            next_score = max(0, int(round(adjusted_score * 0.9)))
            return next_score, {
                "score_adjustment": next_score - adjusted_score,
                "reason": f"真实利润和预测利润偏差 {error_delta:.2f}，系统已下调信任权重。",
                "trust_weight_adjustment": -0.1,
                "strategy_score_adjustment": -0.1,
                "risk_evaluation_adjustment": "raise",
            }
        return adjusted_score, {
            "score_adjustment": 0,
            "reason": "真实反馈与预测接近，当前不需要调低策略分。",
            "trust_weight_adjustment": 0,
            "strategy_score_adjustment": 0,
            "risk_evaluation_adjustment": "keep",
        }


analyze_service: AnalyzeServiceBase = AnalyzeService()
