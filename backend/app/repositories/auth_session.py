from datetime import UTC, datetime
import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth_session import AuthRefreshToken


class AuthSessionRepository:
    def create(
        self,
        db: Session,
        *,
        user_id: int,
        workspace_id: int | None,
        token_jti: str,
        token: str,
        expires_at: datetime,
    ) -> AuthRefreshToken:
        record = AuthRefreshToken(
            user_id=user_id,
            workspace_id=workspace_id,
            token_jti=token_jti,
            token_hash=self._hash(token),
            status="active",
            expires_at=expires_at,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_active_by_jti(self, db: Session, token_jti: str) -> AuthRefreshToken | None:
        now = datetime.now(UTC)
        stmt = (
            select(AuthRefreshToken)
            .where(AuthRefreshToken.token_jti == token_jti)
            .where(AuthRefreshToken.status == "active")
            .where(AuthRefreshToken.revoked_at.is_(None))
            .where(AuthRefreshToken.expires_at > now)
        )
        return db.scalar(stmt)

    def revoke(self, db: Session, record: AuthRefreshToken) -> AuthRefreshToken:
        record.status = "revoked"
        record.revoked_at = datetime.now(UTC)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def revoke_by_token(self, db: Session, token: str) -> AuthRefreshToken | None:
        payload = None
        try:
            from app.core.security import decode_access_token

            payload = decode_access_token(token)
        except Exception:
            return None
        token_jti = str(payload.get("jti") or "").strip()
        if not token_jti:
            return None
        record = self.get_active_by_jti(db, token_jti)
        if not record:
            return None
        return self.revoke(db, record)

    def touch(self, db: Session, record: AuthRefreshToken) -> AuthRefreshToken:
        record.last_used_at = datetime.now(UTC)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


auth_session_repository = AuthSessionRepository()
