from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError, error_response
from app.schemas.product import AnalyzeFullBlockedResponse, AnalyzeFullRequest, AnalyzeFullResponse
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
    response_model=AnalyzeFullResponse | AnalyzeFullBlockedResponse,
)
async def analyze_full_public(
    payload: AnalyzeFullRequest,
    db: Session = Depends(db_session),
):
    try:
        result = await product_service.analyze_full(db, payload.url, None, payload.lang)
        return result
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PUBLIC_ANALYZE_FAILED", str(exc), "ai", status.HTTP_500_INTERNAL_SERVER_ERROR)
