from __future__ import annotations

from datetime import UTC, datetime, timedelta
import os
import resource
import socket

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.api_key.service import api_key_service
from app.billing.order import BillingOrder
from app.billing.plan import PLANS
from app.billing.service import billing_service
from app.billing.subscription import WorkspaceSubscription
from app.core.config import settings
from app.core.runtime import AppError, LOG_FILE
from app.core.startup_checks import collect_runtime_summary
from app.models.data_governance import SyncJobRecord
from app.models.request_metric import RequestMetricRecord
from app.models.user import User
from app.quota.model import WorkspaceQuota
from app.repositories.user import user_repository
from app.workspace.model import Workspace


router = APIRouter()


def _ensure_admin(current_user: User):
    if not current_user.is_superuser and getattr(current_user, "role", "") not in {"owner", "admin"}:
        raise AppError("ADMIN_DENIED", "你没有后台查看权限", "admin", 403)


def _subscription_map(db: Session) -> dict[int, WorkspaceSubscription]:
    rows = list(db.scalars(select(WorkspaceSubscription)))
    return {item.workspace_id: item for item in rows}


def _quota_map(db: Session) -> dict[int, WorkspaceQuota]:
    rows = list(db.scalars(select(WorkspaceQuota)))
    return {item.workspace_id: item for item in rows}


def _parse_fallback_count(hours: int = 24) -> int:
    if not LOG_FILE.exists():
        return 0
    cutoff = datetime.now() - timedelta(hours=hours)
    count = 0
    try:
      with LOG_FILE.open("r", encoding="utf-8", errors="ignore") as handle:
          for line in handle:
              if "ANALYZE_FALLBACK" not in line:
                  continue
              try:
                  stamp = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
              except Exception:
                  continue
              if stamp >= cutoff:
                  count += 1
    except Exception:
        return 0
    return count


def _network_status() -> str:
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=1):
            return "online"
    except Exception:
        return "offline"


def _provider_status(env_key: str) -> str:
    return "OK" if bool((os.getenv(env_key) or "").strip()) else "FAIL"


def _as_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


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

    recent_users = list(db.scalars(select(User).order_by(User.created_at.desc()).limit(8)))
    recent_workspaces = list(db.scalars(select(Workspace).order_by(Workspace.created_at.desc()).limit(8)))
    recent_tasks = list(db.scalars(select(SyncJobRecord).order_by(SyncJobRecord.updated_at.desc()).limit(12)))
    quotas = list(db.scalars(select(WorkspaceQuota).order_by(WorkspaceQuota.updated_at.desc()).limit(12)))
    subscriptions = list(db.scalars(select(WorkspaceSubscription).order_by(WorkspaceSubscription.updated_at.desc()).limit(12)))
    recent_orders = list(db.scalars(select(BillingOrder).order_by(BillingOrder.updated_at.desc()).limit(12)))

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


@router.get("/admin/users")
def get_admin_users(
    search: str | None = Query(default=None),
    plan_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)

    users = user_repository.list_all(db)
    subscription_map = _subscription_map(db)
    quota_map = _quota_map(db)

    items = []
    for item in users:
        subscription = subscription_map.get(item.workspace_id or -1)
        quota = quota_map.get(item.workspace_id or -1)
        member_level = subscription.plan_name if subscription else "free"
        row = {
            "user_id": item.id,
            "contact": item.email,
            "registered_at": item.created_at.isoformat(),
            "member_level": member_level,
            "api_call_count": quota.used_api if quota else 0,
            "status": "active" if item.is_active else "banned",
            "last_login_at": item.last_login_at.isoformat() if item.last_login_at else None,
            "workspace_id": item.workspace_id,
        }
        if search:
            key = search.strip().lower()
            if key not in str(item.id).lower() and key not in (item.email or "").lower():
                continue
        if plan_name and row["member_level"] != plan_name:
            continue
        if status and row["status"] != status:
            continue
        items.append(row)

    return {"items": items}


@router.post("/admin/users/{user_id}/ban")
def ban_user(
    user_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise AppError("USER_NOT_FOUND", "没有找到这个用户", "admin", 404)
    user.is_active = False
    user_repository.save(db, user)
    return {"success": True, "user_id": user_id, "status": "banned"}


@router.post("/admin/users/{user_id}/unban")
def unban_user(
    user_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise AppError("USER_NOT_FOUND", "没有找到这个用户", "admin", 404)
    user.is_active = True
    user_repository.save(db, user)
    return {"success": True, "user_id": user_id, "status": "active"}


@router.post("/admin/users/{user_id}/membership")
def change_user_membership(
    user_id: int,
    payload: dict = Body(...),
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)
    plan_name = str(payload.get("plan_name") or "").strip()
    if plan_name not in PLANS:
        raise AppError("PLAN_NOT_FOUND", "没有找到这个会员等级", "admin", 404)
    user = user_repository.get_by_id(db, user_id)
    if not user or not user.workspace_id:
        raise AppError("USER_NOT_FOUND", "没有找到这个用户或工作区", "admin", 404)
    subscription = billing_service.get_or_create_subscription(db, workspace_id=user.workspace_id)
    subscription.plan_name = plan_name
    subscription.status = "active"
    db.add(subscription)
    db.commit()
    billing_service.apply_plan_quota(db, workspace_id=user.workspace_id)
    return {"success": True, "user_id": user_id, "plan_name": plan_name}


@router.post("/admin/users/{user_id}/reset-api-key")
def reset_user_api_key(
    user_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)
    user = user_repository.get_by_id(db, user_id)
    if not user or not user.workspace_id:
        raise AppError("USER_NOT_FOUND", "没有找到这个用户或工作区", "admin", 404)
    record = api_key_service.reset_user_keys(db, workspace_id=user.workspace_id, user_id=user.id)
    return {"success": True, "user_id": user_id, "api_key_id": record.id, "api_key": record.key}


@router.get("/admin/revenue")
def get_admin_revenue(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    plan_name: str | None = Query(default=None),
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)

    stmt = select(BillingOrder).order_by(BillingOrder.updated_at.desc())
    if user_id is not None:
        stmt = stmt.where(BillingOrder.user_id == user_id)
    if plan_name:
        stmt = stmt.where(BillingOrder.plan_name == plan_name)
    if start_date:
        stmt = stmt.where(BillingOrder.updated_at >= datetime.fromisoformat(start_date))
    if end_date:
        stmt = stmt.where(BillingOrder.updated_at <= datetime.fromisoformat(end_date))

    orders = list(db.scalars(stmt))
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    paid_orders = [item for item in orders if item.status == "paid"]
    today_revenue = sum(
        item.amount_cents for item in paid_orders if _as_utc_datetime(item.updated_at) >= today_start
    )
    month_revenue = sum(
        item.amount_cents for item in paid_orders if _as_utc_datetime(item.updated_at) >= month_start
    )
    total_revenue = sum(item.amount_cents for item in paid_orders)

    return {
        "summary": {
            "today_revenue_cents": today_revenue,
            "month_revenue_cents": month_revenue,
            "total_revenue_cents": total_revenue,
        },
        "items": [
            {
                "order_id": item.id,
                "user_id": item.user_id,
                "member_type": item.plan_name,
                "amount_cents": item.amount_cents,
                "payment_method": item.provider_name,
                "status": item.status,
                "updated_at": item.updated_at.isoformat(),
            }
            for item in orders
        ],
    }


@router.get("/admin/system-status")
def get_admin_system_status(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)

    runtime = collect_runtime_summary()
    since = datetime.now(UTC) - timedelta(hours=24)
    metrics = list(
        db.scalars(
            select(RequestMetricRecord).where(RequestMetricRecord.created_at >= since)
        )
    )
    total_requests = len(metrics)
    avg_response_time = round(sum(item.duration_ms for item in metrics) / total_requests, 2) if total_requests else 0
    error_requests = sum(1 for item in metrics if item.status_code >= 500)
    error_rate = round((error_requests / total_requests) * 100, 2) if total_requests else 0

    return {
        "ai_system": {
            "gateway": "Healthy" if runtime["services"]["ai"] == "ok" else "Down",
            "deepseek": _provider_status("DEEPSEEK_API_KEY"),
            "openai": "OK" if bool((settings.openai_api_key or os.getenv("OPENAI_API_KEY") or "").strip()) else "FAIL",
            "qwen": _provider_status("DASHSCOPE_API_KEY"),
        },
        "api_status": {
            "average_response_ms": avg_response_time,
            "error_rate_percent": error_rate,
            "fallback_count_24h": _parse_fallback_count(24),
            "request_count_24h": total_requests,
        },
        "server_status": {
            "cpu_load_1m": round(os.getloadavg()[0], 2) if hasattr(os, "getloadavg") else 0,
            "memory_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
            "network_status": _network_status(),
        },
        "core_services": runtime["services"],
    }
