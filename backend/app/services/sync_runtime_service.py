from __future__ import annotations

import asyncio
import threading
from collections import defaultdict
from typing import Any, Awaitable, Callable

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.data_governance import data_lineage_repository
from app.repositories.data_governance import sync_job_repository
from app.sync import sync_executor, sync_scheduler


class SyncRuntimeService:
    def __init__(self) -> None:
        self.result_store: dict[int, dict] = {}
        self.latest_job_by_key: dict[str, int] = {}
        self.active_tasks: dict[int, asyncio.Task] = {}
        self.waiters: dict[int, list[asyncio.Event]] = defaultdict(list)

    def submit_sync_task(
        self,
        *,
        db: Session,
        job_type: str,
        job_key: str,
        payload: dict,
        user_id: int | None = None,
        workspace_id: int | None = None,
        api_key_id: int | None = None,
        runner_factory: Callable[[int, Session], Callable[[], Awaitable[dict] | dict]],
    ) -> dict:
        persisted = sync_scheduler.persist_job(
            db,
            job_type=job_type,
            status="pending",
            retry_count=0,
            user_id=user_id,
            workspace_id=workspace_id,
            api_key_id=api_key_id,
        )
        task_id = persisted["id"]
        self.latest_job_by_key[job_key] = task_id

        async def _background():
            background_db = SessionLocal()
            try:
                runner = runner_factory(task_id, background_db)
                result = await sync_executor.execute(
                    db=background_db,
                    task_id=task_id,
                    job_type=job_type,
                    payload=payload,
                    runner=runner,
                )
                self.result_store[task_id] = result
                for waiter in self.waiters.pop(task_id, []):
                    waiter.set()
            finally:
                background_db.close()

        def _run_background() -> None:
            asyncio.run(_background())

        thread = threading.Thread(target=_run_background, daemon=True, name=f"sync-task-{task_id}")
        thread.start()
        self.active_tasks[task_id] = None
        return {"task_id": task_id, "status": "pending", "job_type": job_type}

    def resubmit_existing_task(
        self,
        *,
        db: Session,
        task_id: int,
        job_type: str,
        job_key: str,
        payload: dict,
        runner_factory: Callable[[int, Session], Callable[[], Awaitable[dict] | dict]],
    ) -> dict:
        self.latest_job_by_key[job_key] = task_id
        sync_scheduler.update_persisted_job(db, record_id=task_id, status="retrying", retry_count=0, last_error=None, result_payload=None)

        async def _background():
            background_db = SessionLocal()
            try:
                runner = runner_factory(task_id, background_db)
                result = await sync_executor.execute(
                    db=background_db,
                    task_id=task_id,
                    job_type=job_type,
                    payload=payload,
                    runner=runner,
                )
                self.result_store[task_id] = result
                for waiter in self.waiters.pop(task_id, []):
                    waiter.set()
            finally:
                background_db.close()

        def _run_background() -> None:
            asyncio.run(_background())

        thread = threading.Thread(target=_run_background, daemon=True, name=f"sync-task-retry-{task_id}")
        thread.start()
        self.active_tasks[task_id] = None
        return {"task_id": task_id, "status": "retrying", "job_type": job_type}

    def get_task_status(self, db: Session, task_id: int) -> dict:
        recent = sync_scheduler.update_persisted_job
        del recent  # avoid lint-style unused warnings in runtime-free environment
        from app.repositories.data_governance import sync_job_repository

        record = sync_job_repository.list_recent(db, limit=500)
        row = next((item for item in record if item.id == task_id), None)
        if not row:
            return {"task_id": task_id, "status": "unknown"}
        return {
            "task_id": task_id,
            "status": row.status,
            "retry_count": row.retry_count,
            "last_error": row.last_error,
            "updated_at": row.updated_at.isoformat(),
        }

    async def wait_for_result(self, task_id: int, timeout: float = 15.0) -> dict | None:
        if task_id in self.result_store:
            return self.result_store[task_id]
        event = asyncio.Event()
        self.waiters[task_id].append(event)
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        return self.result_store.get(task_id)

    def get_task_result(self, task_id: int) -> dict | None:
        return self.result_store.get(task_id)

    def get_persisted_task_result(self, db: Session, task_id: int) -> dict | None:
        row = sync_job_repository.get_by_id(db, task_id)
        if not row or not row.result_payload:
            return None
        result_payload = dict(row.result_payload)
        trace_payload = dict(result_payload.get("governance_trace", {}) or {})
        event_key = f"{task_id}:trace:trace_result_persist"
        lineage_record = data_lineage_repository.get_by_event_key(db, event_key)
        if lineage_record:
            trace_payload.update(
                {
                    "event_id": lineage_record.event_id,
                    "event_key": lineage_record.event_key,
                    "event_stage": lineage_record.event_stage,
                    "task_id": lineage_record.task_id,
                    "workspace_id": lineage_record.workspace_id,
                    "user_id": lineage_record.user_id,
                    "api_key_id": lineage_record.api_key_id,
                }
            )
            result_payload["governance_trace"] = trace_payload
        return {
            "job_id": task_id,
            "status": row.status,
            "retry_count": row.retry_count,
            "result": result_payload,
        }


sync_runtime_service = SyncRuntimeService()
