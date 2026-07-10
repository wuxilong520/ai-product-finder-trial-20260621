from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.analysis_orchestrator import analysis_orchestrator
from app.core.business_opportunity_engine import business_opportunity_engine
from app.core.contracts import ProfitBreakdown
from app.core.runtime import AppError, error_response
from app.schemas.opportunity import OpportunityAnalyzeRequest, OpportunityAnalyzeResponse
from app.services.decision_service import decision_service
from app.services.profit_truth_engine import profit_truth_engine


router = APIRouter()


def _build_rule_based_decision(
    *,
    keyword: str,
    market: str,
    business_opportunity: dict,
    supply_intelligence: dict,
    real_profit: dict,
) -> dict:
    recommendation = str(business_opportunity.get("recommendation") or "WATCH")
    if recommendation == "BUY":
        verdict = "go"
        action_level = "SCALE"
    elif recommendation == "TEST":
        verdict = "watch"
        action_level = "TEST"
    elif recommendation == "WATCH":
        verdict = "ignore"
        action_level = "WATCH"
    else:
        verdict = "ignore"
        action_level = "WATCH"
    execution_block_reason = ""
    if action_level == "WATCH":
        execution_block_reason = "当前商业机会分不足，先观察，不建议直接执行。"
    return {
        "keyword": keyword,
        "market": market,
        "verdict": verdict,
        "confidence_score": int(round(float(business_opportunity.get("confidence") or 0) * 100)),
        "recommended_price": 0.0,
        "risk_level": "high" if "low_profit_margin" in business_opportunity.get("risk_flags", []) else "medium",
        "reasons": [
            f"商业机会综合分 {business_opportunity.get('opportunity_score')}",
            f"市场分 {business_opportunity.get('market_score')}，Amazon 分 {business_opportunity.get('amazon_score')}。",
            f"供应分 {business_opportunity.get('supplier_score')}，利润率 {business_opportunity.get('profit_margin')}%。",
            "当前由真实规则引擎给出决策，因为外部 AI 网关暂时不可用。",
        ],
        "decision_score": float(business_opportunity.get("opportunity_score") or 0),
        "strategy_mode": "sourcing",
        "trust_adjusted_score": float(business_opportunity.get("opportunity_score") or 0),
        "real_profit_estimate": float(real_profit.get("real_profit_estimate") or 0),
        "action_plan": ["先看市场", "再看供应", "最后看利润是否达标"],
        "execution_steps": ["验证市场", "验证供应", "验证利润"],
        "feedback_keys": [],
        "trusted_market_data": {},
        "supply_validation": ["确认供应价", "确认 MOQ", "确认交期"],
        "supplier_quality": str(supply_intelligence.get("supplier_quality") or ""),
        "supplier_confidence": float(supply_intelligence.get("supplier_confidence") or 0),
        "real_supply_cost": float((supply_intelligence.get("cost_estimate") or {}).get("landed_cost") or 0),
        "supplier_risk": list(supply_intelligence.get("supplier_risk") or supply_intelligence.get("risk_flags") or []),
        "listing_recommendation": "先测试再决定是否放量" if action_level == "TEST" else "先观察",
        "business_constraints": {},
        "data_trust": {},
        "action_level": action_level,
        "execution_allowed": action_level in {"TEST", "SCALE"},
        "execution_block_reason": execution_block_reason,
        "safety_gate_result": {"allowed": action_level in {"TEST", "SCALE"}, "blocked_reasons": [] if action_level in {"TEST", "SCALE"} else [execution_block_reason], "final_listing_permission": False},
        "final_listing_permission": False,
        "override_history": [],
        "platform_execution_status": "blocked" if action_level == "WATCH" else "queued",
        "execution_bridge_mapping": {},
        "execution_queue_status": "idle" if action_level == "WATCH" else "queued",
        "feedback_signal": {},
        "ai_adjustment_suggestion": {"reason": "等待 AI 网关恢复后再补充 AI 解释层。"},
        "commercial_ready": False,
        "product_mode": "demo_mode",
        "launch_blockers": [],
        "scale_recommendation": "当前先不要自动上架",
    }


@router.post("/opportunity/analyze", response_model=OpportunityAnalyzeResponse)
def analyze_opportunity(
    payload: OpportunityAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del db, auth_context
    try:
        analysis_bundle = analysis_orchestrator.build_analysis_context(
            keyword=payload.keyword,
            market=payload.marketplace or payload.region,
        )
        market_intelligence = analysis_bundle.get("market_intelligence") or {}
        amazon_signal = ((market_intelligence.get("platform_signals") or {}).get("amazon")) or {}
        supply_intelligence = analysis_bundle.get("supply_intelligence") or {}
        cost_estimate = supply_intelligence.get("cost_estimate") or {}
        selected_supplier = supply_intelligence.get("selected_supplier") or {}
        estimated_sell_price = float(cost_estimate.get("suggested_price") or cost_estimate.get("target_price") or 0)
        if estimated_sell_price <= 0:
            shopify_activity = float(((market_intelligence.get("platform_signals") or {}).get("shopify") or {}).get("category_activity") or 0)
            estimated_sell_price = round(max(39.9, shopify_activity * 0.8 + 39.9), 2)
        profit_breakdown = ProfitBreakdown(
            currency="USD",
            cost_price=float(cost_estimate.get("product_cost") or selected_supplier.get("price_mid") or 0),
            selling_price=estimated_sell_price,
            estimated_sell_price=estimated_sell_price,
            supply_cost=float(cost_estimate.get("product_cost") or selected_supplier.get("price_mid") or 0),
            shipping_cost=float(cost_estimate.get("shipping_estimate") or 0),
            platform_fee=float(cost_estimate.get("platform_fee") or 0),
            ad_cost=float(cost_estimate.get("marketing_cost") or 0),
            profit=float((supply_intelligence.get("profit_preview") or {}).get("estimated_profit") or 0),
            margin=float((supply_intelligence.get("profit_preview") or {}).get("margin_rate") or 0),
            break_even_price=float(cost_estimate.get("break_even_price") or 0),
            estimated_profit=float((supply_intelligence.get("profit_preview") or {}).get("estimated_profit") or 0),
            estimated_margin_rate=float((supply_intelligence.get("profit_preview") or {}).get("margin_rate") or 0),
            cost_estimate=float(cost_estimate.get("landed_cost") or 0),
            profit_margin=float((supply_intelligence.get("profit_preview") or {}).get("margin_rate") or 0),
            shopify_reference_price=estimated_sell_price,
            alibaba_reference_cost=float(cost_estimate.get("product_cost") or 0),
            profit_truth_score=float(supply_intelligence.get("confidence") or 0),
        )
        real_profit = profit_truth_engine.calculate_from_supply_intelligence(
            supply_intelligence=supply_intelligence,
            cost_estimate=cost_estimate,
            selling_price=estimated_sell_price,
            ad_cost=float(cost_estimate.get("marketing_cost") or 0),
            currency_loss=0,
        )
        business_opportunity = business_opportunity_engine.evaluate(
            market_score=float(market_intelligence.get("market_score") or 0),
            amazon_demand=float(amazon_signal.get("demand_score") or 0),
            supplier_quality=float(supply_intelligence.get("supplier_score") or 0),
            profit_margin=float(real_profit.get("real_profit_margin") or real_profit.get("margin_rate") or 0),
            market_confidence=float(market_intelligence.get("confidence") or 0),
            amazon_confidence=float((((market_intelligence.get("data_sources") or {}).get("amazon") or {}).get("confidence") or 0)),
            supplier_confidence=float(supply_intelligence.get("supplier_confidence") or 0),
            profit_confidence=float(real_profit.get("confidence") or 0),
            statuses={
                "market": "partial" if float(market_intelligence.get("confidence") or 0) < 1 else "real",
                "amazon": str((((market_intelligence.get("data_sources") or {}).get("amazon") or {}).get("source_status") or "unavailable")),
                "supply": "partial" if float(supply_intelligence.get("supplier_confidence") or 0) < 0.85 else "real",
                "profit": "real_estimate",
            },
        )
        try:
            decision = decision_service.decide(
                keyword=payload.keyword,
                market=payload.marketplace or payload.region,
                profit=profit_breakdown,
                strategy_mode="sourcing",
                analysis_context={
                    **analysis_bundle.get("analysis_context", {}),
                    "market_score": market_intelligence.get("market_score"),
                    "amazon_signal": amazon_signal,
                    "business_opportunity": business_opportunity,
                    "supply_intelligence": supply_intelligence,
                    "supply_context": analysis_bundle.get("supply_context", {}),
                    "cost_context": cost_estimate,
                },
                data_trust={
                    "overall": {
                        "trust_level": min(
                            1.0,
                            max(
                                0.0,
                                (
                                    float(market_intelligence.get("confidence") or 0)
                                    + float(supply_intelligence.get("supplier_confidence") or 0)
                                    + float(real_profit.get("confidence") or 0)
                                ) / 3,
                            ),
                        ),
                        "confidence": float(business_opportunity.get("confidence") or 0),
                        "is_mock": bool(market_intelligence.get("is_mock")) or bool(supply_intelligence.get("is_mock")) or bool(real_profit.get("is_mock_cost")),
                        "is_expired": False,
                        "source_type": "partial",
                    },
                    "data_trust_score": float(business_opportunity.get("confidence") or 0),
                },
                business_constraints={
                    "selling_price": estimated_sell_price,
                    "platform_fee": float(cost_estimate.get("platform_fee") or 0),
                    "shipping_cost": float(cost_estimate.get("shipping_estimate") or 0),
                    "ad_cost": float(cost_estimate.get("marketing_cost") or 0),
                    "product_cost": float(cost_estimate.get("product_cost") or 0),
                    "currency_loss": 0,
                },
            ).model_dump(mode="json")
        except Exception:
            decision = _build_rule_based_decision(
                keyword=payload.keyword,
                market=payload.marketplace or payload.region,
                business_opportunity=business_opportunity,
                supply_intelligence=supply_intelligence,
                real_profit=real_profit,
            )
        return OpportunityAnalyzeResponse(
            keyword=payload.keyword,
            marketplace=payload.marketplace,
            region=payload.region,
            market_score=float(business_opportunity["market_score"]),
            amazon_score=float(business_opportunity["amazon_score"]),
            supplier_score=float(business_opportunity["supplier_score"]),
            profit_margin=float(business_opportunity["profit_margin"]),
            opportunity_score=float(business_opportunity["opportunity_score"]),
            recommendation=str(business_opportunity["recommendation"]),
            confidence=float(business_opportunity["confidence"]),
            risk_flags=list(business_opportunity["risk_flags"]),
            market_status="partial" if float(market_intelligence.get("confidence") or 0) < 1 else "real",
            amazon_status=str((((market_intelligence.get("data_sources") or {}).get("amazon") or {}).get("source_status") or "unavailable")),
            supply_status="partial" if float(supply_intelligence.get("supplier_confidence") or 0) < 0.85 else "real",
            profit_status="real_estimate",
            amazon_signal=amazon_signal,
            selected_supplier=selected_supplier,
            real_profit=real_profit,
            decision=decision,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("OPPORTUNITY_ANALYZE_FAILED", str(exc), "opportunity", status.HTTP_500_INTERNAL_SERVER_ERROR)
