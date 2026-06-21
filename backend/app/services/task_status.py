from __future__ import annotations

from datetime import UTC, datetime

from app.ws_manager import task_ws_manager


class TaskStatusService:
    def __init__(self) -> None:
        self.status_store: dict[str, dict] = {
            "crawl": self._build_payload("pending", "采集任务待开始"),
            "analyze": self._build_payload("pending", "分析任务待开始"),
        }

    def _build_payload(
        self,
        status: str,
        message: str,
        detail: dict | None = None,
        error_reason: str | None = None,
    ) -> dict:
        return {
            "success": True,
            "status": status,
            "message": message,
            "detail": detail or {},
            "error_reason": error_reason,
            "updated_at": datetime.now(UTC).isoformat(),
        }

    async def update(
        self,
        task_name: str,
        status: str,
        message: str,
        detail: dict | None = None,
        error_reason: str | None = None,
    ) -> dict:
        payload = self._build_payload(status, message, detail, error_reason)
        self.status_store[task_name] = payload
        await task_ws_manager.broadcast(task_name, payload)
        return payload

    def get(self, task_name: str) -> dict:
        return self.status_store.get(task_name, self._build_payload("unknown", "没有这个任务状态"))


task_status_service = TaskStatusService()
