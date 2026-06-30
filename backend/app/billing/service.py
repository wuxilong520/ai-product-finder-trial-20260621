from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.billing.plan import PLANS
from app.billing.subscription import WorkspaceSubscription
from app.quota.service import quota_service


class BillingService:
    def get_or_create_subscription(self, db: Session, *, workspace_id: int) -> WorkspaceSubscription:
        stmt = select(WorkspaceSubscription).where(WorkspaceSubscription.workspace_id == workspace_id)
        record = db.scalar(stmt)
        if record:
            return record
        record = WorkspaceSubscription(workspace_id=workspace_id, plan_name="free", status="active")
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def apply_plan_quota(self, db: Session, *, workspace_id: int) -> WorkspaceSubscription:
        subscription = self.get_or_create_subscription(db, workspace_id=workspace_id)
        plan = PLANS.get(subscription.plan_name, PLANS["free"])
        quota = quota_service.get_or_create(
            db,
            workspace_id=workspace_id,
            daily_task_limit=plan["task_limit"],
            daily_api_limit=plan["api_limit"],
        )
        quota.daily_task_limit = plan["task_limit"]
        quota.daily_api_limit = plan["api_limit"]
        db.add(quota)
        db.commit()
        return subscription


billing_service = BillingService()
