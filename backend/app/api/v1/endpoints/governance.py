from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.services.data_governance_query_service import data_governance_query_service


router = APIRouter()


@router.get("/governance/lineage/{record_id}")
def get_governance_lineage(
    record_id: str,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return {"items": data_governance_query_service.get_lineage(db, record_id, workspace_id=auth_context.workspace_id)}
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("GOVERNANCE_LINEAGE_FAILED", str(exc), "governance", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/governance/trust/{record_id}")
def get_governance_trust(
    record_id: str,
    truth_level: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    freshness: float | None = Query(default=None),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        market = data_governance_query_service.get_trusted_market_signals(
            db,
            workspace_id=auth_context.workspace_id,
            truth_level=truth_level,
            source_type=source_type,
            freshness_min=freshness,
        )
        supplier = data_governance_query_service.get_supplier_offers(
            db,
            workspace_id=auth_context.workspace_id,
            truth_level=truth_level,
            source_type=source_type,
            freshness_min=freshness,
        )
        return {"record_id": record_id, "market": market, "supplier": supplier}
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("GOVERNANCE_TRUST_FAILED", str(exc), "governance", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/governance/source/{record_id}")
def get_governance_source(
    record_id: str,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return {"record_id": record_id, "sources": data_governance_query_service.get_source_breakdown(db, workspace_id=auth_context.workspace_id)}
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("GOVERNANCE_SOURCE_FAILED", str(exc), "governance", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/governance/quality/{record_id}")
def get_governance_quality(
    record_id: str,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return {"record_id": record_id, "expired": data_governance_query_service.get_expired_data(db, workspace_id=auth_context.workspace_id)}
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("GOVERNANCE_QUALITY_FAILED", str(exc), "governance", status.HTTP_500_INTERNAL_SERVER_ERROR)
