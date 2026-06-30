from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from sqlalchemy.orm import Session

from app.sync.retry_queue import retry_queue
from app.sync.scheduler import sync_scheduler


class SyncExecutor:
    async def execute(
        self,
        *,
        db: Session,
        task_id: int,
        job_type: str,
        payload: dict,
        runner: Callable[[], Awaitable[dict] | dict],
        max_retries: int = 2,
    ) -> dict:
        record_id = task_id
        sync_scheduler.update_persisted_job(
            db,
            record_id=record_id,
            status="running",
            retry_count=0,
            result_payload={"task_input": payload},
        )

        retry_count = 0
        while True:
            try:
                result = runner()
                if asyncio.iscoroutine(result):
                    result = await result
                sync_scheduler.update_persisted_job(
                    db,
                    record_id=record_id,
                    status="success",
                    retry_count=retry_count,
                    result_payload={**({"task_input": payload} if isinstance(payload, dict) else {}), **(result if isinstance(result, dict) else {"result": result})},
                )
                return {
                    "job_id": record_id,
                    "status": "success",
                    "retry_count": retry_count,
                    "result": result,
                }
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                retry_count += 1
                if retry_count <= max_retries:
                    retry_queue.push({"job_type": job_type, "payload": payload, "retry_count": retry_count, "error": str(exc)})
                    sync_scheduler.update_persisted_job(
                        db,
                        record_id=record_id,
                        status="running",
                        retry_count=retry_count,
                        last_error=str(exc),
                        result_payload={"task_input": payload},
                    )
                    await asyncio.sleep(0)
                    continue

                sync_scheduler.update_persisted_job(
                    db,
                    record_id=record_id,
                    status="failed",
                    retry_count=retry_count,
                    last_error=str(exc),
                    result_payload={"task_input": payload, "last_error": str(exc)},
                )
                return {
                    "job_id": record_id,
                    "status": "failed",
                    "retry_count": retry_count,
                    "error": str(exc),
                }


sync_executor = SyncExecutor()
