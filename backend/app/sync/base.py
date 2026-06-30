from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


class SyncJobBase:
    def __init__(self, provider: str) -> None:
        self.job_id = str(uuid4())
        self.provider = provider
        self.status = "pending"
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.error_message: str | None = None

    def run(self):
        self.status = "running"
        self.updated_at = datetime.now(timezone.utc)

    def retry(self):
        self.status = "retrying"
        self.updated_at = datetime.now(timezone.utc)

    def fail(self, error_message: str):
        self.status = "failed"
        self.error_message = error_message
        self.updated_at = datetime.now(timezone.utc)

    def success(self):
        self.status = "success"
        self.updated_at = datetime.now(timezone.utc)
