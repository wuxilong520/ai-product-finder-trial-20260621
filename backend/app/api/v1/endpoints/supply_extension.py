from __future__ import annotations

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.supply_extension import (
    SupplyExtensionCodeResponse,
    SupplyExtensionImportResponse,
    SupplyExtensionSessionRequest,
    SupplyExtensionSessionResponse,
    SupplyImportPayload,
)
from app.services.supply_extension_gateway import supply_extension_gateway


router = APIRouter()


@router.post("/supply/extension/code", response_model=SupplyExtensionCodeResponse)
def create_supply_extension_code(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        return supply_extension_gateway.generate_extension_code(
            db,
            user_id=auth_context.user_id,
            workspace_id=auth_context.workspace_id,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLY_EXTENSION_CODE_FAILED", str(exc), "supply_extension", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/supply/extension/session", response_model=SupplyExtensionSessionResponse)
def create_supply_extension_session(
    payload: SupplyExtensionSessionRequest,
    db: Session = Depends(db_session),
):
    try:
        return supply_extension_gateway.exchange_extension_code(db, extension_code=payload.extension_code)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLY_EXTENSION_SESSION_FAILED", str(exc), "supply_extension", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/supply/extension/import", response_model=SupplyExtensionImportResponse)
def import_supply_extension_payload(
    payload: SupplyImportPayload,
    authorization: str | None = Header(default=None),
    db: Session = Depends(db_session),
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return error_response("SUPPLY_EXTENSION_TOKEN_MISSING", "插件还没连接商航AI，请先输入连接码。", "supply_extension", status.HTTP_401_UNAUTHORIZED)
        raw_token = authorization.removeprefix("Bearer ").strip()
        token_payload = supply_extension_gateway.validate_extension_token(db, raw_token=raw_token)
        return supply_extension_gateway.import_payload(db, token_payload=token_payload, payload=payload)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLY_EXTENSION_IMPORT_FAILED", str(exc), "supply_extension", status.HTTP_500_INTERNAL_SERVER_ERROR)
