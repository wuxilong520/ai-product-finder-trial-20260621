from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError
from app.schemas.opportunity import (
    OpportunityAnalyzeRequest,
    OpportunityAnalyzeResponse,
    OpportunityExecuteRequest,
    OpportunityExecuteResponse,
    OpportunityHistoryResponse,
)
from app.services.business_opportunity_v3_service import business_opportunity_v3_service


router = APIRouter()


@router.post("/opportunity/analyze", response_model=OpportunityAnalyzeResponse)
def analyze_opportunity(
    payload: OpportunityAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    result = business_opportunity_v3_service.analyze(
        db,
        keyword=payload.keyword,
        market=payload.marketplace or payload.region,
    )
    return OpportunityAnalyzeResponse.model_validate(result.model_dump(mode="json"))


@router.post("/opportunity/execute", response_model=OpportunityExecuteResponse)
def execute_opportunity(
    payload: OpportunityExecuteRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    if not str(payload.shop_domain or "").strip():
        raise AppError("SHOP_DOMAIN_REQUIRED", "执行 Shopify 草稿前必须先传店铺域名", "opportunity", 400)

    result = business_opportunity_v3_service.execute(
        db,
        keyword=payload.keyword,
        market=payload.marketplace or payload.region,
        shop_domain=payload.shop_domain,
    )
    return OpportunityExecuteResponse.model_validate(result)


@router.get("/opportunity/history", response_model=OpportunityHistoryResponse)
def get_opportunity_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    records = business_opportunity_v3_service.history(db, limit=limit)
    return OpportunityHistoryResponse(items=records)
