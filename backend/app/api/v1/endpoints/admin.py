from sqlalchemy import func, select
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError
from app.models.data_governance import SyncJobRecord
from app.models.user import User
from app.quota.model import WorkspaceQuota
from app.billing.subscription import WorkspaceSubscription
from app.billing.order import BillingOrder
from app.workspace.model import Workspace


router = APIRouter()


def _ensure_admin(current_user: User):
    if not current_user.is_superuser and getattr(current_user, "role", "") not in {"owner", "admin"}:
        raise AppError("ADMIN_DENIED", "你没有后台查看权限", "admin", 403)


@router.get("/admin/overview")
def get_admin_overview(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)

    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    total_workspaces = db.scalar(select(func.count()).select_from(Workspace)) or 0
    total_tasks = db.scalar(select(func.count()).select_from(SyncJobRecord)) or 0
    paid_workspaces = db.scalar(
        select(func.count()).select_from(WorkspaceSubscription).where(WorkspaceSubscription.plan_name != "free")
    ) or 0
    free_workspaces = db.scalar(
        select(func.count()).select_from(WorkspaceSubscription).where(WorkspaceSubscription.plan_name == "free")
    ) or 0
    running_tasks = db.scalar(
        select(func.count()).select_from(SyncJobRecord).where(SyncJobRecord.status == "running")
    ) or 0
    failed_tasks = db.scalar(
        select(func.count()).select_from(SyncJobRecord).where(SyncJobRecord.status == "failed")
    ) or 0
    total_orders = db.scalar(select(func.count()).select_from(BillingOrder)) or 0
    paid_orders = db.scalar(
        select(func.count()).select_from(BillingOrder).where(BillingOrder.status == "paid")
    ) or 0
    revenue_cents = db.scalar(
        select(func.coalesce(func.sum(BillingOrder.amount_cents), 0)).where(BillingOrder.status == "paid")
    ) or 0

    recent_users = list(
        db.scalars(select(User).order_by(User.created_at.desc()).limit(8))
    )
    recent_workspaces = list(
        db.scalars(select(Workspace).order_by(Workspace.created_at.desc()).limit(8))
    )
    recent_tasks = list(
        db.scalars(select(SyncJobRecord).order_by(SyncJobRecord.updated_at.desc()).limit(12))
    )
    quotas = list(
        db.scalars(select(WorkspaceQuota).order_by(WorkspaceQuota.updated_at.desc()).limit(12))
    )
    subscriptions = list(
        db.scalars(select(WorkspaceSubscription).order_by(WorkspaceSubscription.updated_at.desc()).limit(12))
    )
    recent_orders = list(
        db.scalars(select(BillingOrder).order_by(BillingOrder.updated_at.desc()).limit(12))
    )

    return {
        "summary": {
            "total_users": total_users,
            "total_workspaces": total_workspaces,
            "total_tasks": total_tasks,
            "paid_workspaces": paid_workspaces,
            "free_workspaces": free_workspaces,
            "running_tasks": running_tasks,
            "failed_tasks": failed_tasks,
            "total_orders": total_orders,
            "paid_orders": paid_orders,
            "revenue_cents": revenue_cents,
        },
        "recent_users": [
            {
                "id": item.id,
                "email": item.email,
                "full_name": item.full_name,
                "role": item.role,
                "workspace_id": item.workspace_id,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat(),
            }
            for item in recent_users
        ],
        "recent_workspaces": [
            {
                "id": item.id,
                "name": item.name,
                "owner_id": item.owner_id,
                "created_at": item.created_at.isoformat(),
            }
            for item in recent_workspaces
        ],
        "recent_tasks": [
            {
                "id": item.id,
                "job_type": item.job_type,
                "status": item.status,
                "retry_count": item.retry_count,
                "workspace_id": item.workspace_id,
                "user_id": item.user_id,
                "updated_at": item.updated_at.isoformat(),
                "last_error": item.last_error,
            }
            for item in recent_tasks
        ],
        "quota_snapshots": [
            {
                "workspace_id": item.workspace_id,
                "daily_task_limit": item.daily_task_limit,
                "daily_api_limit": item.daily_api_limit,
                "used_task": item.used_task,
                "used_api": item.used_api,
                "updated_at": item.updated_at.isoformat(),
            }
            for item in quotas
        ],
        "subscription_snapshots": [
            {
                "workspace_id": item.workspace_id,
                "plan_name": item.plan_name,
                "status": item.status,
                "updated_at": item.updated_at.isoformat(),
            }
            for item in subscriptions
        ],
        "recent_orders": [
            {
                "id": item.id,
                "workspace_id": item.workspace_id,
                "user_id": item.user_id,
                "plan_name": item.plan_name,
                "status": item.status,
                "amount_cents": item.amount_cents,
                "currency": item.currency,
                "provider_name": item.provider_name,
                "updated_at": item.updated_at.isoformat(),
            }
            for item in recent_orders
        ],
    }
