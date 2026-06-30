from __future__ import annotations

from collections import deque

from sqlalchemy.orm import Session

from app.repositories.data_governance import sync_job_repository


class SyncScheduler:
    def __init__(self) -> None:
        self.queue: deque[dict] = deque()
        self.failures: deque[dict] = deque()

    def add_manual_trigger(self, job_type: str, payload: dict, priority: str = "normal") -> dict:
        item = {"job_type": job_type, "payload": payload, "priority": priority}
        self.queue.append(item)
        return item

    def add_failure_retry(self, job_type: str, payload: dict) -> dict:
        item = {"job_type": job_type, "payload": payload, "priority": "retry"}
        self.failures.append(item)
        return item

    def list_queue(self) -> list[dict]:
        return list(self.queue)

    def list_failures(self) -> list[dict]:
        return list(self.failures)

    def persist_job(
        self,
        db: Session,
        *,
        job_type: str,
        status: str,
        retry_count: int = 0,
        last_error: str | None = None,
        user_id: int | None = None,
        workspace_id: int | None = None,
        api_key_id: int | None = None,
    ) -> dict:
        record = sync_job_repository.create(
            db,
            job_type=job_type,
            status=status,
            retry_count=retry_count,
            last_error=last_error,
            user_id=user_id,
            workspace_id=workspace_id,
            api_key_id=api_key_id,
        )
        return {
            "id": record.id,
            "job_type": record.job_type,
            "status": record.status,
            "retry_count": record.retry_count,
            "last_error": record.last_error,
            "user_id": record.user_id,
            "workspace_id": record.workspace_id,
            "api_key_id": record.api_key_id,
        }

    def update_persisted_job(
        self,
        db: Session,
        *,
        record_id: int,
        status: str,
        retry_count: int | None = None,
        last_error: str | None = None,
        result_payload: dict | None = None,
    ) -> dict | None:
        record = sync_job_repository.update_status(
            db,
            record_id,
            status=status,
            retry_count=retry_count,
            last_error=last_error,
            result_payload=result_payload,
        )
        if not record:
            return None
        return {
            "id": record.id,
            "job_type": record.job_type,
            "status": record.status,
            "retry_count": record.retry_count,
            "last_error": record.last_error,
        }


sync_scheduler = SyncScheduler()
