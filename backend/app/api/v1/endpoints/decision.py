from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError, error_response
from app.schemas.decision import DecisionRecommendRequest, DecisionRecommendResponse
from app.services.decision_engine import decision_engine


router = APIRouter()


@router.post("/decision/recommend", response_model=DecisionRecommendResponse)
def recommend_decision(
    payload: DecisionRecommendRequest,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    try:
        result = decision_engine.recommend(db, payload.product_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("DECISION_ENGINE_FAILED", str(exc), "decision", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return DecisionRecommendResponse(**result)
