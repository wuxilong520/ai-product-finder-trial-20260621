from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_connection import DataConnection


class DataConnectionRepository:
    def list_by_user(self, db: Session, *, user_id: int) -> list[DataConnection]:
        stmt = select(DataConnection).where(DataConnection.user_id == user_id).order_by(DataConnection.created_at.desc(), DataConnection.id.desc())
        return list(db.scalars(stmt))

    def get_by_user_platform(self, db: Session, *, user_id: int, platform: str, workspace_id: int | None = None) -> DataConnection | None:
        stmt = select(DataConnection).where(DataConnection.user_id == user_id, DataConnection.platform == platform)
        if workspace_id is not None:
            stmt = stmt.where(DataConnection.workspace_id == workspace_id)
        return db.scalar(stmt)

    def upsert(
        self,
        db: Session,
        *,
        user_id: int,
        workspace_id: int | None = None,
        platform: str,
        status: str,
        encrypted_access_token: str,
        encrypted_refresh_token: str,
        expires_at,
        permission_scope: list[str],
        shop_domain: str | None = None,
        external_account_id: str | None = None,
        connection_meta: dict | None = None,
        last_synced_at=None,
        last_sync_error: str | None = None,
    ) -> DataConnection:
        existing = self.get_by_user_platform(db, user_id=user_id, platform=platform, workspace_id=workspace_id)
        if existing:
            existing.status = status
            existing.encrypted_access_token = encrypted_access_token
            existing.encrypted_refresh_token = encrypted_refresh_token
            existing.expires_at = expires_at
            existing.permission_scope = permission_scope
            existing.shop_domain = shop_domain
            existing.external_account_id = external_account_id
            existing.connection_meta = connection_meta or existing.connection_meta or {}
            existing.last_synced_at = last_synced_at
            existing.last_sync_error = last_sync_error
            if workspace_id is not None:
                existing.workspace_id = workspace_id
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        record = DataConnection(
            user_id=user_id,
            workspace_id=workspace_id,
            platform=platform,
            status=status,
            encrypted_access_token=encrypted_access_token,
            encrypted_refresh_token=encrypted_refresh_token,
            expires_at=expires_at,
            permission_scope=permission_scope,
            shop_domain=shop_domain,
            external_account_id=external_account_id,
            connection_meta=connection_meta or {},
            last_synced_at=last_synced_at,
            last_sync_error=last_sync_error,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def revoke(self, db: Session, *, user_id: int, platform: str, workspace_id: int | None = None) -> DataConnection | None:
        record = self.get_by_user_platform(db, user_id=user_id, platform=platform, workspace_id=workspace_id)
        if not record:
            return None
        record.status = "REVOKED"
        record.encrypted_access_token = ""
        record.encrypted_refresh_token = ""
        record.permission_scope = []
        record.connection_meta = {}
        record.last_sync_error = None
        if workspace_id is not None:
            record.workspace_id = workspace_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def touch_sync(
        self,
        db: Session,
        *,
        record: DataConnection,
        status: str | None = None,
        last_synced_at=None,
        last_sync_error: str | None = None,
        connection_meta: dict | None = None,
    ) -> DataConnection:
        if status is not None:
            record.status = status
        record.last_synced_at = last_synced_at
        record.last_sync_error = last_sync_error
        if connection_meta is not None:
            record.connection_meta = connection_meta
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


data_connection_repository = DataConnectionRepository()
