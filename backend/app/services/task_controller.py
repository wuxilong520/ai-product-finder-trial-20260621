from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.middleware.auth_middleware import RequestAuthContext
from app.quota.service import quota_service
from app.repositories.data_governance import sync_job_repository
from app.services.sync_runtime_service import sync_runtime_service


class TaskController:
    def get_task_record(self, db: Session, task_id: int):
        return sync_job_repository.get_by_id(db, task_id)

    def submit_task(
        self,
        db: Session,
        *,
        job_type: str,
        job_key: str,
        payload: dict,
        auth_context: RequestAuthContext,
        runner_factory: Callable[[int, Session], Callable[[], dict]],
    ) -> dict:
        quota_service.consume_task(db, workspace_id=auth_context.workspace_id)
        task = sync_runtime_service.submit_sync_task(
            db=db,
            job_type=job_type,
            job_key=job_key,
            payload=payload,
            user_id=auth_context.user_id,
            workspace_id=auth_context.workspace_id,
            api_key_id=auth_context.api_key_id,
            runner_factory=runner_factory,
        )
        if "task_id" not in task:
            raise AppError("TASK_SUBMIT_FAILED", "任务提交失败", "task", 500)
        return task

    def get_task_status(self, db: Session, task_id: int) -> dict:
        return sync_runtime_service.get_task_status(db, task_id)

    def get_task_result(self, db: Session, task_id: int) -> dict | None:
        return sync_runtime_service.get_task_result(task_id) or sync_runtime_service.get_persisted_task_result(db, task_id)

    def list_tasks(self, db: Session, *, auth_context: RequestAuthContext) -> list[dict]:
        rows = sync_job_repository.list_all(db, limit=200, workspace_id=auth_context.workspace_id)
        items: list[dict] = []
        for row in rows:
            status = row.status
            progress = 100 if status in {"success", "failed"} else 65 if status == "running" else 15 if status == "pending" else 40
            items.append(
                {
                    "task_id": row.id,
                    "status": status,
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat(),
                    "retry_count": row.retry_count,
                    "progress": progress,
                    "last_error": row.last_error,
                    "workspace_id": row.workspace_id,
                    "user_id": row.user_id,
                }
            )
        return items

    def retry_task(
        self,
        db: Session,
        *,
        task_id: int,
        runner_factory: Callable[[int, Session], Callable[[], dict]],
    ) -> dict:
        record = sync_job_repository.get_by_id(db, task_id)
        if not record:
            raise AppError("TASK_NOT_FOUND", "没有找到这个任务", "task", 404)

        payload = record.result_payload or {}
        decision_result = payload.get("decision_result", {}) if isinstance(payload.get("decision_result", {}), dict) else {}
        explain_result = payload.get("explain_result", {}) if isinstance(payload.get("explain_result", {}), dict) else {}
        trace_result = payload.get("governance_trace", {}) if isinstance(payload.get("governance_trace", {}), dict) else {}
        product_id = payload.get("product_id") or decision_result.get("product_id") or explain_result.get("product_id") or 1
        task_payload = {
            "product_id": product_id,
            "keyword": payload.get("keyword") or decision_result.get("keyword") or "",
            "market_type": payload.get("market_type") or trace_result.get("provider_routing", {}).get("market_type") or "amazon",
            "supplier_strategy": payload.get("supplier_strategy") or trace_result.get("provider_routing", {}).get("supplier_strategy") or "balanced",
            "cost_mode": payload.get("cost_mode") or trace_result.get("provider_routing", {}).get("cost_mode") or "estimated",
            "decision_mode": payload.get("decision_mode") or "deep",
            "user_id": record.user_id,
            "workspace_id": record.workspace_id,
            "api_key_id": record.api_key_id,
        }
        return sync_runtime_service.resubmit_existing_task(
            db=db,
            task_id=task_id,
            job_type=record.job_type,
            job_key=f"{record.job_type}:{task_id}",
            payload=task_payload,
            runner_factory=runner_factory,
        )


task_controller = TaskController()
