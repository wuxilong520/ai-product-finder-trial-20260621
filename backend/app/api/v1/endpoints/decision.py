import asyncio

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.ai_engine import ai_engine
from app.core.runtime import AppError, error_response
from app.schemas.skeleton_v1 import ApiEnvelope, DecisionV1Request
from app.services.analyze_service import analyze_service
from app.services.decision_service import decision_service
from app.services.explain_engine import explain_engine
from app.schemas.decision import DecisionRecommendRequest, DecisionRecommendResponse
from app.services.sync_runtime_service import sync_runtime_service
from app.services.task_controller import task_controller
from app.sync.execution_bridge import execution_bridge


router = APIRouter()


@router.post("/decision", response_model=ApiEnvelope)
def decision_v1(payload: DecisionV1Request):
    analysis = analyze_service.analyze(keyword=payload.keyword, market=payload.market)
    decision = decision_service.decide(
        keyword=payload.keyword,
        market=payload.market,
        profit=analysis.profit_breakdown,
        strategy_mode=payload.strategy_mode,
        analysis_context={
            "keyword": payload.keyword,
            "market": payload.market,
            "market_summary": analysis.market_insight.summary,
            "suggested_price": analysis.profit_breakdown.estimated_sell_price,
            "estimated_profit": analysis.profit_breakdown.estimated_profit,
            "estimated_margin_rate": analysis.profit_breakdown.estimated_margin_rate,
            "analysis_score": analysis.analysis_outcome.score,
            "market_score": analysis.market_insight.market_score,
            "trusted_market_data": {
                "market_score": analysis.market_insight.market_score,
                "recommendation": analysis.market_insight.recommendation,
                "confidence": analysis.market_insight.confidence,
            },
            "supply_intelligence": analysis.trust_report.get("supply_intelligence", {}),
            "supply_context": analysis.trust_report.get("supply_context", {}),
            "cost_context": analysis.trust_report.get("cost_context", {}),
        },
        data_trust=analysis.trust_report,
        business_constraints=payload.business_constraints,
    )
    explain = explain_engine.build(decision=decision, profit=analysis.profit_breakdown)
    return ApiEnvelope(
        data={
            "analysis": analysis.model_dump(mode="json"),
            "decision": decision.model_dump(mode="json"),
            "explain": explain.model_dump(mode="json"),
        },
        meta={
            "version": "shanghang-ai-v1",
            "ai_engine": getattr(ai_engine, "engine_name", "unknown"),
        },
    )


@router.post("/decision/recommend", response_model=DecisionRecommendResponse)
def recommend_decision(
    payload: DecisionRecommendRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        task = task_controller.submit_task(
            db,
            job_type="decision",
            job_key=f"decision:{payload.product_id}",
            payload={"product_id": payload.product_id},
            auth_context=auth_context,
            runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
                task_db,
                task_id=task_id,
                job_type="decision",
                payload={"product_id": payload.product_id, "workspace_id": auth_context.workspace_id, "user_id": auth_context.user_id},
            ),
        )
        result_wrapper = sync_runtime_service.get_task_result(task["task_id"])
        if not result_wrapper:
            result_wrapper = asyncio.run(sync_runtime_service.wait_for_result(task["task_id"], timeout=15))
        if not result_wrapper or result_wrapper.get("status") != "success":
            return error_response("DECISION_PENDING", "决策任务仍在执行，请稍后重试。", "decision", status.HTTP_202_ACCEPTED)
        result = result_wrapper["result"]["decision_result"] if "decision_result" in result_wrapper.get("result", {}) else result_wrapper["result"]
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("DECISION_ENGINE_FAILED", str(exc), "decision", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return DecisionRecommendResponse(**result)
