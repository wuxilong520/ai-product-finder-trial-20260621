from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.ai_engine import ai_engine
from app.core.contracts import AnalysisOutcome, MarketInsight, ProfitBreakdown, SupplyOffer


class AnalysisEngineBase(ABC):
    @abstractmethod
    def run(
        self,
        *,
        keyword: str,
        market_data: MarketInsight,
        supply_data: list[SupplyOffer],
        cost_data: ProfitBreakdown,
        trend_data: list[dict],
        competition_data: dict,
        plan_name: str = "free",
    ) -> AnalysisOutcome:
        raise NotImplementedError


class AnalysisEngine(AnalysisEngineBase):
    def _normalize_score(self, ai_result: dict) -> int:
        raw_score = ai_result.get("score")
        if raw_score is None:
            raw_score = ai_result.get("decision_score")
        if raw_score is None:
            raw_score = ai_result.get("trust_adjusted_score")
        if raw_score is None:
            raw_score = ai_result.get("confidence_score")
        try:
            normalized = int(round(float(raw_score)))
        except (TypeError, ValueError):
            normalized = 0
        return max(0, min(100, normalized))

    def _normalize_recommend(self, ai_result: dict, *, score: int) -> bool:
        if "recommend" in ai_result:
            return bool(ai_result["recommend"])
        verdict = str(ai_result.get("verdict", "")).strip().lower()
        return verdict in {"go", "buy", "test", "scale", "auto_list"} or score >= 70

    def _normalize_risk(self, ai_result: dict) -> str:
        return str(ai_result.get("risk", ai_result.get("risk_level", "medium")))

    def _normalize_profit_estimate(self, ai_result: dict, *, fallback_profit: float) -> float:
        raw_profit = ai_result.get("profit_estimate")
        if raw_profit is None:
            raw_profit = ai_result.get("real_profit_estimate")
        if raw_profit is None:
            raw_profit = fallback_profit
        try:
            return float(raw_profit)
        except (TypeError, ValueError):
            return float(fallback_profit)

    def _normalize_reasoning(self, ai_result: dict) -> str:
        if ai_result.get("reasoning"):
            return str(ai_result["reasoning"])
        reasons = ai_result.get("reasons")
        if isinstance(reasons, list) and reasons:
            return "；".join(str(item) for item in reasons if item)
        return "AI 已完成结构化分析。"

    def _normalize_action(self, ai_result: dict, *, recommend: bool) -> str:
        if ai_result.get("action"):
            return str(ai_result["action"])
        verdict = str(ai_result.get("verdict", "")).strip().lower()
        if verdict in {"go", "buy", "scale", "auto_list"}:
            return "list"
        if verdict in {"watch", "test"}:
            return "test"
        return "ignore" if not recommend else "list"

    def _resolve_model_tier(self, *, plan_name: str) -> str:
        normalized = (plan_name or "free").strip().lower()
        if normalized == "enterprise":
            return "priority"
        if normalized == "pro":
            return "high"
        if normalized == "plus":
            return "mid"
        return "cheap"

    def run(
        self,
        *,
        keyword: str,
        market_data: MarketInsight,
        supply_data: list[SupplyOffer],
        cost_data: ProfitBreakdown,
        trend_data: list[dict],
        competition_data: dict,
        plan_name: str = "free",
    ) -> AnalysisOutcome:
        selected_supply = supply_data[0] if supply_data else None
        model_tier = self._resolve_model_tier(plan_name=plan_name)
        ai_result = ai_engine.complete_json(
            task_name="analysis",
            system_prompt="你是商航AI的市场分析引擎，只返回结构化 JSON。",
            user_prompt=f"请分析关键词 {keyword} 是否适合进入下一步商业验证。",
            context={
                "keyword": keyword,
                "market": market_data.market,
                "market_data": market_data.model_dump(mode="json"),
                "selected_supply": selected_supply.model_dump(mode="json") if selected_supply else None,
                "cost_data": cost_data.model_dump(mode="json"),
                "trend_data": trend_data,
                "competition_data": competition_data,
                "model_tier": model_tier,
                "plan_name": plan_name,
            },
        )
        normalized_score = self._normalize_score(ai_result)
        normalized_recommend = self._normalize_recommend(ai_result, score=normalized_score)
        return AnalysisOutcome(
            score=normalized_score,
            recommend=normalized_recommend,
            risk=self._normalize_risk(ai_result),
            profit_estimate=self._normalize_profit_estimate(ai_result, fallback_profit=cost_data.estimated_profit),
            reasoning=self._normalize_reasoning(ai_result),
            action=self._normalize_action(ai_result, recommend=normalized_recommend),
            trace=[*list(ai_result.get("trace", [])), f"model_tier:{model_tier}", f"plan:{plan_name}"],
        )


analysis_engine: AnalysisEngineBase = AnalysisEngine()
