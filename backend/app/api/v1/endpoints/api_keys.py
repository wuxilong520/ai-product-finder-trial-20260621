from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.api_key.service import api_key_service


router = APIRouter()


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
