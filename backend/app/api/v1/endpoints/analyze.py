from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.skeleton_v1 import AnalyzeV1Request, ApiEnvelope
from app.services.analyze_service import analyze_service
from app.schemas.product import AnalyzeFullBlockedResponse, AnalyzeFullRequest, AnalyzeFullResponse
from app.services.product import product_service


router = APIRouter()


@router.post("/analyze", response_model=ApiEnvelope)
def analyze_v1(payload: AnalyzeV1Request):
    result = analyze_service.analyze(keyword=payload.keyword, market=payload.market)
    return ApiEnvelope(
        data=result.model_dump(mode="json"),
        meta={
            "version": "shanghang-ai-v1",
            "ai_engine": "mock_ai_engine",
            "market_adapter": result.market_insight.source,
            "supply_adapter": result.selected_offer.source,
        },
    )


@router.post(
    "/analyze/full",
    response_model=AnalyzeFullResponse | AnalyzeFullBlockedResponse,
)
async def analyze_full(
    payload: AnalyzeFullRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        result = await product_service.analyze_full(
            db,
            payload.url,
            auth_context.user_id,
            payload.lang,
            workspace_id=auth_context.workspace_id,
        )
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
        result = await product_service.analyze_full(db, payload.url, None, payload.lang, workspace_id=None)
        return result
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PUBLIC_ANALYZE_FAILED", str(exc), "ai", status.HTTP_500_INTERNAL_SERVER_ERROR)
