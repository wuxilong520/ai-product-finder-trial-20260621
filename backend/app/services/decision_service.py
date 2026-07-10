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
    def _extract_supply_inputs(
        self,
        *,
        analysis_context: dict,
        profit: ProfitBreakdown,
    ) -> dict:
        supply_intelligence = analysis_context.get("supply_intelligence") or {}
        supply_context = analysis_context.get("supply_context") or {}
        cost_context = analysis_context.get("cost_context") or {}
        real_cost = float(cost_context.get("landed_cost") or cost_context.get("product_cost") or profit.supply_cost)
        margin = float(cost_context.get("margin") or profit.estimated_margin_rate)
        supplier_score = float(
            supply_context.get("supplier_score")
            or supply_intelligence.get("supplier_score")
            or 0
        )
        supplier_quality = str(
            supply_context.get("supplier_quality")
            or supply_intelligence.get("supplier_quality")
            or "not_recommended"
        )
        supplier_confidence = float(
            supply_context.get("supplier_confidence")
            or supply_intelligence.get("supplier_confidence")
            or 0
        )
        if "risk_flags" in supply_context:
            supplier_risk = list(supply_context.get("risk_flags") or [])
        elif "supplier_risk" in supply_intelligence:
            supplier_risk = list(supply_intelligence.get("supplier_risk") or [])
        else:
            supplier_risk = list(supply_intelligence.get("risk_flags") or [])
        return {
            "supply_intelligence": supply_intelligence,
            "supply_context": supply_context,
            "cost_context": cost_context,
            "real_cost": real_cost,
            "margin": margin,
            "supplier_score": supplier_score,
            "supplier_quality": supplier_quality,
            "supplier_confidence": supplier_confidence,
            "supplier_risk": supplier_risk,
        }

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
        supply_inputs = self._extract_supply_inputs(
            analysis_context=normalized_analysis_context,
            profit=profit,
        )
        trusted_market_data = normalized_analysis_context.get("trusted_market_data") or {}
        amazon_signal = normalized_analysis_context.get("amazon_signal") or trusted_market_data.get("amazon_signal") or {}
        business_opportunity = normalized_analysis_context.get("business_opportunity") or {}
        normalized_constraints["product_cost"] = float(
            (business_constraints or {}).get("product_cost", supply_inputs["real_cost"])
        )
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
                "supplier_quality": supply_inputs["supplier_quality"],
                "supplier_score": supply_inputs["supplier_score"],
                "supplier_confidence": supply_inputs["supplier_confidence"],
                "supplier_risk": supply_inputs["supplier_risk"],
                "real_cost": supply_inputs["real_cost"],
                "margin": supply_inputs["margin"],
                "amazon_signal": amazon_signal,
                "opportunity_score": business_opportunity.get("opportunity_score"),
            },
        )
        truth_profit = profit_truth_engine.calculate_from_supply_intelligence(
            supply_intelligence=supply_inputs["supply_intelligence"],
            cost_estimate=supply_inputs["cost_context"],
            selling_price=float(normalized_constraints["selling_price"]),
            ad_cost=float(normalized_constraints["ad_cost"]),
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
        reasons.append(
            f"供应商评分 {supply_inputs['supplier_score']:.2f}，供应质量 {supply_inputs['supplier_quality']}，供应可信度 {supply_inputs['supplier_confidence']:.2f}，落地成本 {supply_inputs['real_cost']:.2f}。"
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
        market_confidence = float(trusted_market_data.get("confidence") or normalized_analysis_context.get("confidence") or 0)
        desired_action_level = None
        watch_block_reason = ""
        amazon_demand = float(amazon_signal.get("demand_score") or 0)
        if amazon_demand > 0:
            reasons.append(f"Amazon 竞争验证需求分 {amazon_demand:.2f}，评论量 {int(amazon_signal.get('review_count') or 0)}，卖家数 {int(amazon_signal.get('seller_count') or 0)}。")
        opportunity_score = float(business_opportunity.get("opportunity_score") or 0)
        if opportunity_score > 0:
            reasons.append(f"商业机会综合分 {opportunity_score:.2f}，推荐 {business_opportunity.get('recommendation') or 'WATCH'}。")
            if opportunity_score < 40:
                verdict = "ignore"
                desired_action_level = "WATCH"
                watch_block_reason = "商业机会综合分低于 40，当前只建议观察，不建议直接执行。"
            elif opportunity_score >= 75 and desired_action_level not in {"WATCH", "TEST"}:
                desired_action_level = "SCALE"
        if bool(trusted_market_data.get("all_sources_mock")):
            verdict = "watch"
            risk_level = "high"
            reasons.append("市场侧当前全部是 mock 来源，系统强制把最高动作限制在 WATCH。")
            watch_block_reason = "市场数据全部是 mock，当前只能 WATCH。"
        if supply_inputs["supplier_confidence"] < 0.6:
            desired_action_level = "TEST"
            reasons.append("供应商可信度低于 0.6，禁止进入 AUTO_LIST，当前最多只能 TEST。")
        if bool(trusted_market_data.get("all_sources_mock")) or market_confidence <= 0.3:
            desired_action_level = "WATCH"
            watch_block_reason = "市场可信度过低，当前只能 WATCH。"
        market_score = float((normalized_analysis_context.get("trusted_market_data") or {}).get("market_score") or normalized_analysis_context.get("market_score") or 0)
        if (
            supply_inputs["supplier_score"] > 80
            and float(supply_inputs["margin"] or 0) > 0.3
            and market_score > 70
        ):
            desired_action_level = "SCALE"
            reasons.append("供应商评分、利润率、市场分数都达标，可以进入 SCALE。")
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
            supplier_quality=supply_inputs["supplier_quality"],
            supplier_confidence=supply_inputs["supplier_confidence"],
            real_supply_cost=supply_inputs["real_cost"],
            supplier_risk=supply_inputs["supplier_risk"],
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
        if desired_action_level == "WATCH" and execution_result["action_level"] != "WATCH":
            execution_result["override_history"].append({
                "rule": "market_all_mock_or_low_confidence_watch_only",
                "from": execution_result["action_level"],
                "to": "WATCH",
            })
            execution_result["action_level"] = "WATCH"
            execution_result["execution_block_reason"] = watch_block_reason or "当前只允许观察，不允许直接执行。"
        if desired_action_level == "TEST" and execution_result["action_level"] in {"SCALE", "AUTO_LIST"}:
            execution_result["override_history"].append({
                "rule": "supplier_confidence_lt_0.6",
                "from": execution_result["action_level"],
                "to": "TEST",
            })
            execution_result["action_level"] = "TEST"
            execution_result["execution_block_reason"] = "供应商可信度低于 0.6，禁止进入 AUTO_LIST。"
        if (
            desired_action_level == "SCALE"
            and execution_result["action_level"] == "TEST"
            and not overall_trust.get("is_mock", False)
            and float(overall_trust.get("trust_level", 0)) >= 0.6
            and str(decision.risk_level).lower() != "high"
        ):
            execution_result["override_history"].append({
                "rule": "supplier_market_margin_scale_ready",
                "from": execution_result["action_level"],
                "to": "SCALE",
            })
            execution_result["action_level"] = "SCALE"
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
