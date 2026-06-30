from __future__ import annotations

import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api_key.model import ApiKeyRecord


class ApiKeyService:
    def create_key(self, db: Session, *, workspace_id: int, user_id: int) -> ApiKeyRecord:
        record = ApiKeyRecord(
            key=f"cbp_{secrets.token_urlsafe(24)}",
            workspace_id=workspace_id,
            user_id=user_id,
            status="active",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_by_key(self, db: Session, raw_key: str) -> ApiKeyRecord | None:
        stmt = select(ApiKeyRecord).where(ApiKeyRecord.key == raw_key)
        return db.scalar(stmt)


api_key_service = ApiKeyService()
