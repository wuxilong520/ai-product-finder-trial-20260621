from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.services.decision_explain_service import decision_explain_service


router = APIRouter()


@router.get("/decision/explain/{decision_id}")
def get_decision_explain(
    decision_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        result = decision_explain_service.explain(
            db,
            decision_id,
            task_input={
                "user_id": auth_context.user_id,
                "workspace_id": auth_context.workspace_id,
                "api_key_id": auth_context.api_key_id,
            },
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("DECISION_EXPLAIN_FAILED", str(exc), "decision", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return {
        "decision_id": decision_id,
        "market_signals_used": result.get("market_signals_used", []),
        "supplier_sources": result.get("supplier_sources", []),
        "cost_breakdown": result.get("cost_breakdown", {}),
        "risk_factors": result.get("risk_factors", []),
        "confidence_score": result.get("confidence_score", 0),
        "why_this_recommendation": result.get("why_this_recommendation", []),
        "data_lineage": result.get("data_lineage", []),
        "provider_routing": result.get("provider_routing", {}),
    }
