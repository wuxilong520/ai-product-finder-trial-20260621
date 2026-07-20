from __future__ import annotations

from app.core.database import SessionLocal
from app.services.sync.shopify_sync_service import shopify_sync_service


class ShopifySyncTask:
    def run_first_sync(self, *, user_id: int, workspace_id: int | None) -> dict:
        db = SessionLocal()
        try:
            return shopify_sync_service.sync_connection(db, user_id=user_id, workspace_id=workspace_id, reason="first_sync")
        finally:
            db.close()

    def run_scheduled_sync(self, *, user_id: int, workspace_id: int | None) -> dict:
        db = SessionLocal()
        try:
            return shopify_sync_service.sync_connection(db, user_id=user_id, workspace_id=workspace_id, reason="scheduled_sync")
        finally:
            db.close()

    def retry_failed(self) -> list[dict]:
        db = SessionLocal()
        try:
            return shopify_sync_service.retry_failed_syncs(db)
        finally:
            db.close()


shopify_sync_task = ShopifySyncTask()
