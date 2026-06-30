from __future__ import annotations

from sqlalchemy.orm import Session

from app.api_key.service import api_key_service


class ApiKeyValidator:
    def validate(self, db: Session, raw_key: str):
        if not raw_key:
            return None
        record = api_key_service.get_by_key(db, raw_key)
        if not record or record.status != "active":
            return None
        return record


api_key_validator = ApiKeyValidator()
