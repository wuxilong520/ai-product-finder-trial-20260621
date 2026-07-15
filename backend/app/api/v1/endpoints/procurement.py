from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.procurement import (
    ProcurementAnalyzeResponse,
    ProcurementCompareResponse,
    ProcurementFavoriteRequest,
    ProcurementFavoriteResponse,
    ProcurementImportPayload,
    ProcurementImportResponse,
    ProcurementPoolItemResponse,
    ProcurementPoolListResponse,
)
from app.services.procurement_pool_service import procurement_pool_service


router = APIRouter()


def _parse_range(raw: str | None) -> tuple[float | None, float | None] | None:
    if not raw:
        return None
    parts = [part.strip() for part in str(raw).split(",")]
    if not parts:
        return None
    left = float(parts[0]) if parts[0] else None
    right = float(parts[1]) if len(parts) > 1 and parts[1] else None
    return left, right


@router.get("/procurement/pool", response_model=ProcurementPoolListResponse)
def get_procurement_pool(
    keyword: str | None = Query(default=None),
    category: str | None = Query(default=None),
    price_range: str | None = Query(default=None),
    profit_range: str | None = Query(default=None),
    supplier_score: float | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    sort: str = Query(default="latest"),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return procurement_pool_service.list_pool(
            db,
            user_id=auth_context.user_id,
            workspace_id=auth_context.workspace_id,
            keyword=keyword,
            category=category,
            price_range=_parse_range(price_range),
            profit_range=_parse_range(profit_range),
            supplier_score=supplier_score,
            risk_level=risk_level,
            sort=sort,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PROCUREMENT_POOL_FAILED", str(exc), "procurement", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/procurement/product/{pool_item_id}", response_model=ProcurementPoolItemResponse)
def get_procurement_product(
    pool_item_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return procurement_pool_service.get_pool_item(db, user_id=auth_context.user_id, pool_item_id=pool_item_id, workspace_id=auth_context.workspace_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PROCUREMENT_PRODUCT_FAILED", str(exc), "procurement", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/procurement/import", response_model=ProcurementImportResponse)
def import_procurement_payload(
    payload: ProcurementImportPayload,
    authorization: str | None = Header(default=None),
    db: Session = Depends(db_session),
):
    try:
        user_id, workspace_id = procurement_pool_service.resolve_user_context_from_token(db, authorization=authorization)
        result = procurement_pool_service.import_from_extension_payload(
            db,
            user_id=user_id,
            workspace_id=workspace_id,
            payload=payload.model_dump(mode="json"),
        )
        return {
            "imported": True,
            "pool_item_id": int(result["pool_item_id"]),
            "created": bool(result["created"]),
        }
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PROCUREMENT_IMPORT_FAILED", str(exc), "procurement", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/procurement/analyze/{pool_item_id}", response_model=ProcurementAnalyzeResponse)
def analyze_procurement_item(
    pool_item_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return procurement_pool_service.analyze_pool_item(db, user_id=auth_context.user_id, pool_item_id=pool_item_id, workspace_id=auth_context.workspace_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PROCUREMENT_ANALYZE_FAILED", str(exc), "procurement", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/procurement/favorite", response_model=ProcurementFavoriteResponse)
def favorite_procurement_item(
    payload: ProcurementFavoriteRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return procurement_pool_service.favorite(
            db,
            user_id=auth_context.user_id,
            pool_item_id=payload.pool_item_id,
            action=payload.action,
            workspace_id=auth_context.workspace_id,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PROCUREMENT_FAVORITE_FAILED", str(exc), "procurement", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/procurement/compare", response_model=ProcurementCompareResponse)
def compare_procurement_items(
    ids: str = Query(..., min_length=1),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        pool_item_ids = [int(value.strip()) for value in ids.split(",") if value.strip().isdigit()]
        return procurement_pool_service.compare(db, user_id=auth_context.user_id, pool_item_ids=pool_item_ids, workspace_id=auth_context.workspace_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PROCUREMENT_COMPARE_FAILED", str(exc), "procurement", status.HTTP_500_INTERNAL_SERVER_ERROR)
