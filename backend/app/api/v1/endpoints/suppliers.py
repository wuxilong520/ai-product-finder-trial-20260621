from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError, error_response
from app.schemas.supplier import SupplierMatchRequest, SupplierMatchResponse
from app.services.supplier_matching_engine import supplier_matching_engine


router = APIRouter()


@router.post("/suppliers/match", response_model=SupplierMatchResponse)
def match_suppliers(
    payload: SupplierMatchRequest,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    try:
        result = supplier_matching_engine.match(db, payload.keyword)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLIER_MATCH_FAILED", str(exc), "supplier", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return SupplierMatchResponse(**result)
