from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.supplier import SupplierMatchRequest, SupplierMatchResponse
from app.services.supplier_matching_engine import supplier_matching_engine


router = APIRouter()


@router.post("/suppliers/match", response_model=SupplierMatchResponse)
def match_suppliers(
    payload: SupplierMatchRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        result = supplier_matching_engine.match(
            db,
            payload.keyword,
            category=payload.category,
            target_market=payload.target_market,
            expected_price=payload.expected_price,
            quantity=payload.quantity,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLIER_MATCH_FAILED", str(exc), "supplier", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return SupplierMatchResponse(**result)
