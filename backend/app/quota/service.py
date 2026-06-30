from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.quota.model import WorkspaceQuota


class QuotaService:
    def get_or_create(self, db: Session, *, workspace_id: int, daily_task_limit: int = 10, daily_api_limit: int = 100) -> WorkspaceQuota:
        stmt = select(WorkspaceQuota).where(WorkspaceQuota.workspace_id == workspace_id)
        record = db.scalar(stmt)
        if record:
            return record
        record = WorkspaceQuota(
            workspace_id=workspace_id,
            daily_task_limit=daily_task_limit,
            daily_api_limit=daily_api_limit,
            used_task=0,
            used_api=0,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def ensure_task_quota(self, db: Session, *, workspace_id: int) -> WorkspaceQuota:
        quota = self.get_or_create(db, workspace_id=workspace_id)
        if quota.daily_task_limit >= 0 and quota.used_task >= quota.daily_task_limit:
            raise AppError("QUOTA_TASK_EXCEEDED", "今天可用任务次数已经用完", "quota", 403)
        return quota

    def ensure_api_quota(self, db: Session, *, workspace_id: int) -> WorkspaceQuota:
        quota = self.get_or_create(db, workspace_id=workspace_id)
        if quota.daily_api_limit >= 0 and quota.used_api >= quota.daily_api_limit:
            raise AppError("QUOTA_API_EXCEEDED", "今天可用接口次数已经用完", "quota", 403)
        return quota

    def consume_task(self, db: Session, *, workspace_id: int) -> WorkspaceQuota:
        quota = self.ensure_task_quota(db, workspace_id=workspace_id)
        quota.used_task += 1
        db.add(quota)
        db.commit()
        db.refresh(quota)
        return quota

    def consume_api(self, db: Session, *, workspace_id: int) -> WorkspaceQuota:
        quota = self.ensure_api_quota(db, workspace_id=workspace_id)
        quota.used_api += 1
        db.add(quota)
        db.commit()
        db.refresh(quota)
        return quota


quota_service = QuotaService()
