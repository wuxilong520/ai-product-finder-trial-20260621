from __future__ import annotations

from app.sync.base import SyncJobBase


class CostSyncJob(SyncJobBase):
    def __init__(self, provider: str = "cost_pipeline") -> None:
        super().__init__(provider)

    def execute(self, *, region: str, mode: str = "incremental") -> dict:
        self.run()
        return {
            "job_id": self.job_id,
            "provider": self.provider,
            "mode": mode,
            "region": region,
            "status": self.status,
        }
