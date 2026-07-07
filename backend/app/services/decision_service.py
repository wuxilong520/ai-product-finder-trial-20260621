from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.execution_control_layer import execution_control_layer
from app.core.execution_log_layer import execution_log_layer
from app.core.feedback_loop import feedback_loop
from app.core.strategy_layer import strategy_layer
from app.core.audit_logger import audit_logger
from app.core.ai_engine import ai_engine
from app.core.contracts import DecisionRecord, ProfitBreakdown
from app.services.profit_truth_engine import profit_truth_engine
from app.core.feedback_loop_v2 import feedback_loop_v2
from app.core.commercial_readiness_engine import commercial_readiness_engine
from app.core.production_bootstrap_layer import production_bootstrap_layer


class DecisionServiceBase(ABC):
    @abstractmethod
    def decide(
        self,
        *,
        keyword: str,
        market: str,
        profit: ProfitBreakdown,
        strategy_mode: str = "sourcing",
        analysis_context: dict | None = None,
        data_trust: dict | None = None,
        business_constraints: dict | None = None,
    ) -> DecisionRecord:
        raise NotImplementedError


class DecisionService(DecisionServiceBase):
    def _normalize_confidence_score(self, ai_result: dict, *, default_score: float = 50) -> int:
        raw_score = ai_result.get("confidence_score")
        if raw_score is None:
            raw_score = ai_result.get("decision_score")
        if raw_score is None:
            raw_score = ai_result.get("trust_adjusted_score")
        try:
            normalized = int(round(float(raw_score)))
        except (TypeError, ValueError):
            normalized = int(round(float(default_score)))
        return max(0, min(100, normalized))

    def _normalize_trust_adjusted_score(self, ai_result: dict, *, confidence_score: int) -> float:
        raw_score = ai_result.get("trust_adjusted_score")
        if raw_score is None:
            raw_score = ai_result.get("confidence_score")
        if raw_score is None:
            raw_score = ai_result.get("decision_score")
        try:
            return float(raw_score)
        except (TypeError, ValueError):
            return float(confidence_score)

    def _normalize_verdict(self, ai_result: dict, *, confidence_score: int) -> str:
        verdict = str(ai_result.get("verdict", "")).strip().lower()
        if verdict:
            return verdict
        if confidence_score >= 75:
            return "go"
        if confidence_score >= 55:
            return "watch"
        return "ignore"

    def _normalize_risk_level(self, ai_result: dict, *, confidence_score: int) -> str:
        risk_level = str(ai_result.get("risk_level", ai_result.get("risk", ""))).strip().lower()
        if risk_level:
            return risk_level
        if confidence_score >= 75:
            return "low"
        if confidence_score >= 55:
            return "medium"
        return "high"

    def _normalize_reasons(self, ai_result: dict, *, fallback_reason: str) -> list[str]:
        reasons = ai_result.get("reasons")
        if isinstance(reasons, list) and reasons:
            normalized = [str(item) for item in reasons if str(item).strip()]
            if normalized:
                return normalized
        reasoning = str(ai_result.get("reasoning", "")).strip()
        if reasoning:
            return [reasoning]
        return [fallback_reason]

    def decide(
        self,
        *,
        keyword: str,
        market: str,
        profit: ProfitBreakdown,
        strategy_mode: str = "sourcing",
        analysis_context: dict | None = None,
        data_trust: dict | None = None,
        business_constraints: dict | None = None,
    ) -> DecisionRecord:
        normalized_analysis_context = analysis_context or {
            "keyword": keyword,
            "market": market,
            "suggested_price": profit.estimated_sell_price,
            "estimated_profit": profit.estimated_profit,
            "estimated_margin_rate": profit.estimated_margin_rate,
            "market_summary": f"{keyword} 在 {market} 已完成基础分析。",
        }
        normalized_data_trust = data_trust or {
            "trust_level": 0.5,
            "confidence": 0.5,
            "is_mock": True,
            "is_expired": False,
            "source_type": "estimated",
        }
        normalized_constraints = {
            "selling_price": float(normalized_analysis_context.get("suggested_price") or profit.estimated_sell_price),
            "platform_fee": float((business_constraints or {}).get("platform_fee", profit.platform_fee)),
            "shipping_cost": float((business_constraints or {}).get("shipping_cost", profit.shipping_cost)),
            "ad_cost": float((business_constraints or {}).get("ad_cost", profit.ad_cost)),
            "product_cost": float((business_constraints or {}).get("product_cost", profit.supply_cost)),
            "currency_loss": float((business_constraints or {}).get("currency_loss", 0)),
            **(business_constraints or {}),
        }
        strategy_plan = strategy_layer.build(
            strategy_mode=strategy_mode,
            keyword=keyword,
            market=market,
            business_constraints=normalized_constraints,
        )
        overall_trust = normalized_data_trust.get("overall", normalized_data_trust)
        data_trust_score = float(normalized_data_trust.get('data_trust_score', normalized_data_trust.get('platform_data', {}).get('data_trust_score', 0.0)) or 0.0)
        execution_policy = execution_control_layer.build_execution_policy(
            trust_level=float(overall_trust.get("trust_level", 0)),
            is_mock=bool(overall_trust.get("is_mock", False)),
            risk_level="medium",
        )
        ai_result = ai_engine.complete_json(
            task_name="decision",
            system_prompt="你是商航AI的商业决策引擎，只返回结构化 JSON。",
            user_prompt=f"请判断 {keyword} 是否值得在 {market} 做。",
            context={
                "strategy_mode": strategy_plan.strategy_mode,
                "analysis_context": normalized_analysis_context,
                "data_trust": normalized_data_trust.get("overall", normalized_data_trust),
                "business_constraints": normalized_constraints,
                "execution_policy": execution_policy,
                "keyword": keyword,
                "market": market,
                "suggested_price": profit.estimated_sell_price,
                "estimated_profit": profit.estimated_profit,
                "estimated_margin_rate": profit.estimated_margin_rate,
            },
        )
        truth_profit = profit_truth_engine.calculate(
            selling_price=float(normalized_constraints["selling_price"]),
            platform_fee=float(normalized_constraints["platform_fee"]),
            shipping_cost=float(normalized_constraints["shipping_cost"]),
            ad_cost=float(normalized_constraints["ad_cost"]),
            product_cost=float(normalized_constraints["product_cost"]),
            currency_loss=float(normalized_constraints["currency_loss"]),
        )
        feedback_keys = feedback_loop.register_feedback_keys(keyword=keyword, market=market, strategy_mode=strategy_plan.strategy_mode)
        confidence_score = self._normalize_confidence_score(
            ai_result,
            default_score=normalized_analysis_context.get("analysis_score") or 50,
        )
        trust_adjusted_score = self._normalize_trust_adjusted_score(
            ai_result,
            confidence_score=confidence_score,
        )
        is_mock = bool(overall_trust.get("is_mock"))
        if is_mock:
            trust_adjusted_score = round(trust_adjusted_score * 0.72, 2)
        verdict = self._normalize_verdict(ai_result, confidence_score=confidence_score)
        risk_level = self._normalize_risk_level(ai_result, confidence_score=confidence_score)
        listing_recommendation = str(ai_result.get("listing_recommendation", strategy_plan.listing_recommendation))
        reasons = self._normalize_reasons(
            ai_result,
            fallback_reason=f"{keyword} 在 {market} 已完成基础决策分析，但当前 AI 返回缺少完整理由字段。",
        )
        if is_mock:
            verdict = "watch"
            risk_level = "high" if risk_level != "high" else risk_level
            listing_recommendation = "当前是 mock 数据，只能做验证，不允许当成最终上架决策。"
            reasons.append("当前输入含 mock 数据，系统已强制降级为验证结论，不能直接作为最终商业动作。")
        if data_trust_score < 0.6:
            verdict = 'watch'
            listing_recommendation = '当前真实数据可信度不足，先观察，不要直接执行。'
            reasons.append('data_trust_score 低于 0.6，系统已自动降级为 observe。')
        decision_id = f"{strategy_plan.strategy_mode}:{market}:{keyword}".replace(" ", "_").lower()
        latest_feedback = feedback_loop_v2.latest_signal(keyword=keyword, market=market)
        ai_adjustment_suggestion = {
            "decision_id": decision_id,
            "reason": "当前还没有真实执行回写，保持原始决策。",
            "error_delta_threshold": 5.0,
            "next_action": "继续观察真实执行反馈",
        }
        if latest_feedback:
            ai_adjustment_suggestion = {
                "decision_id": decision_id,
                "reason": f"最近一次真实利润偏差为 {abs(float(latest_feedback.get('error_delta') or 0)):.2f}",
                "error_delta_threshold": 5.0,
                "next_action": "偏差大就降低信任权重，偏差小就维持当前策略",
            }
        readiness = commercial_readiness_engine.evaluate()
        bootstrap_status = production_bootstrap_layer.status()
        decision = DecisionRecord(
            keyword=keyword,
            market=market,
            verdict=verdict,
            confidence_score=confidence_score,
            recommended_price=float(ai_result.get("recommended_price", normalized_constraints["selling_price"])),
            risk_level=risk_level,
            reasons=reasons,
            decision_score=float(ai_result.get("decision_score", confidence_score)),
            strategy_mode=str(ai_result.get("strategy_mode", strategy_plan.strategy_mode)),
            trust_adjusted_score=trust_adjusted_score,
            real_profit_estimate=float(ai_result.get("real_profit_estimate", truth_profit["real_profit_estimate"])),
            action_plan=list(ai_result.get("action_plan", strategy_plan.action_plan)),
            execution_steps=list(ai_result.get("execution_steps", strategy_plan.execution_steps)),
            feedback_keys=list(ai_result.get("feedback_keys", feedback_keys)),
            trusted_market_data=dict(ai_result.get("trusted_market_data", normalized_analysis_context)),
            supply_validation=list(ai_result.get("supply_validation", strategy_plan.supply_validation)),
            listing_recommendation=listing_recommendation,
            business_constraints=normalized_constraints,
            data_trust=overall_trust,
            feedback_signal=(latest_feedback.get("feedback_signal") if latest_feedback else {}),
            ai_adjustment_suggestion=ai_adjustment_suggestion,
            commercial_ready=bool(readiness["ready_to_launch"]),
            product_mode=str(bootstrap_status["product_mode"]),
            launch_blockers=list(bootstrap_status["blocking_items"]),
            scale_recommendation=str(readiness["scale_recommendation"]),
        )
        execution_result = execution_control_layer.evaluate(decision)
        decision = decision.model_copy(update=execution_result)
        execution_log_layer.write(
            keyword=keyword,
            market=market,
            decision=decision.model_dump(mode="json"),
            execution_level=decision.action_level,
            blocked_reason=decision.execution_block_reason,
            override_history=decision.override_history,
        )
        audit_logger.write(
            user_id=None,
            action="ai_decision_generated",
            payload=decision.model_dump(mode="json"),
        )
        return decision


decision_service: DecisionServiceBase = DecisionService()
