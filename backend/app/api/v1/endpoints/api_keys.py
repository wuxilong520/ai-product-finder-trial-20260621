from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.api_key.service import api_key_service


router = APIRouter()


def _mask_api_key(raw_key: str) -> str:
    if len(raw_key) <= 12:
        return raw_key
    return f"{raw_key[:8]}...{raw_key[-4:]}"


@router.get("/api-keys")
def list_api_keys(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    records = api_key_service.list_by_user(db, user_id=auth_context.user_id)
    return {
        "items": [
            {
                "id": record.id,
                "workspace_id": record.workspace_id,
                "user_id": record.user_id,
                "status": record.status,
                "masked_key": _mask_api_key(record.key),
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
            }
            for record in records
        ]
    }


@router.post("/api-keys")
def create_api_key(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    record = api_key_service.create_key(
        db,
        workspace_id=auth_context.workspace_id,
        user_id=auth_context.user_id,
    )
    return {
        "id": record.id,
        "key": record.key,
        "workspace_id": record.workspace_id,
        "user_id": record.user_id,
        "status": record.status,
    }
