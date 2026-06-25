from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError, error_response
from app.schemas.market import MarketAnalyzeRequest, MarketAnalyzeResponse
from app.services.market_intelligence_engine import market_intelligence_engine


router = APIRouter()


@router.post("/market/analyze", response_model=MarketAnalyzeResponse)
def analyze_market_keyword(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    try:
        result = market_intelligence_engine.analyze_keyword(db, payload.keyword)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_ANALYZE_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return MarketAnalyzeResponse(**result)
