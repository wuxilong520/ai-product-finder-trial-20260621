from __future__ import annotations

from sqlalchemy.orm import Session

from app.sync.base import SyncJobBase


class SupplierSyncJob(SyncJobBase):
    def __init__(self, provider: str = "supplier_pipeline") -> None:
        super().__init__(provider)

    def execute(self, db: Session, *, keyword: str, mode: str = "incremental") -> dict:
        self.run()
        return {
            "job_id": self.job_id,
            "provider": self.provider,
            "mode": mode,
            "keyword": keyword,
            "status": self.status,
        }
