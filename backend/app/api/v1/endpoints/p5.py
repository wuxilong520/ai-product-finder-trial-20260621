from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.p5 import (
    P5PredictionRequest,
    P5PredictionResponse,
    P5RankingsResponse,
    P5RecommendationsResponse,
)
from app.services.p5_global_product_decision_engine import p5_global_product_decision_engine


router = APIRouter()


@router.get("/p5/recommendations", response_model=P5RecommendationsResponse)
def get_p5_recommendations(
    keyword: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        result = p5_global_product_decision_engine.get_recommendations(db, keyword=keyword, category=category, limit=limit)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("P5_RECOMMENDATIONS_FAILED", str(exc), "p5", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return P5RecommendationsResponse(**result)


@router.get("/p5/rankings", response_model=P5RankingsResponse)
def get_p5_rankings(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        result = p5_global_product_decision_engine.get_rankings(db)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("P5_RANKINGS_FAILED", str(exc), "p5", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return P5RankingsResponse(**result)


@router.post("/p5/predict", response_model=P5PredictionResponse)
def post_p5_predict(
    payload: P5PredictionRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        result = p5_global_product_decision_engine.predict(db, payload.product_id, payload.horizon_days)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("P5_PREDICT_FAILED", str(exc), "p5", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return P5PredictionResponse(**result)
