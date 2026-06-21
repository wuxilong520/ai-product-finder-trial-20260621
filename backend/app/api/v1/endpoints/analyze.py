from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError, error_response
from app.schemas.product import AnalyzeFullBlockedResponse, AnalyzeFullRequest, AnalyzeFullResponse, AnalyzeFullTrialFallbackResponse
from app.services.product import product_service


router = APIRouter()


@router.post(
    "/analyze/full",
    response_model=AnalyzeFullResponse | AnalyzeFullBlockedResponse,
)
async def analyze_full(
    payload: AnalyzeFullRequest,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    try:
        result = await product_service.analyze_full(db, payload.url, current_user.id, payload.lang)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("AI_CALL_FAILED", str(exc), "ai", status.HTTP_502_BAD_GATEWAY)
    return result


@router.post(
    "/analyze/full/public",
    response_model=AnalyzeFullResponse | AnalyzeFullBlockedResponse | AnalyzeFullTrialFallbackResponse,
)
async def analyze_full_public(
    payload: AnalyzeFullRequest,
    db: Session = Depends(db_session),
):
    try:
        result = await product_service.analyze_full(db, payload.url, None, payload.lang)
        return result
    except AppError as exc:
        if exc.error_code in {"AI_CALL_FAILED", "MISSING_OPENAI_KEY", "REAL_AI_FAILED"}:
            return {
                "product_score": "N/A",
                "recommendation": "TRY_LATER",
                "reason": "system_busy",
            }
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception:
        return {
            "product_score": "N/A",
            "recommendation": "TRY_LATER",
            "reason": "system_busy",
        }
