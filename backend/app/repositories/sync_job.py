from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_governance import SyncJobRecord


class SyncJobRepository:
    def create(
        self,
        db: Session,
        *,
        user_id: int | None,
        workspace_id: int | None,
        api_key_id: int | None,
        job_type: str,
        platform: str,
        status: str,
        retry_count: int = 0,
        last_error: str | None = None,
        result_payload: dict | None = None,
        started_at=None,
        finished_at=None,
    ) -> SyncJobRecord:
        record = SyncJobRecord(
            user_id=user_id,
            workspace_id=workspace_id,
            api_key_id=api_key_id,
            job_type=job_type,
            platform=platform,
            status=status,
            retry_count=retry_count,
            last_error=last_error,
            result_payload=result_payload,
            started_at=started_at,
            finished_at=finished_at,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def save(self, db: Session, record: SyncJobRecord) -> SyncJobRecord:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_failed(self, db: Session, *, platform: str, limit: int = 20) -> list[SyncJobRecord]:
        stmt = (
            select(SyncJobRecord)
            .where(SyncJobRecord.platform == platform, SyncJobRecord.status == "ERROR")
            .order_by(SyncJobRecord.updated_at.desc(), SyncJobRecord.id.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt))


sync_job_repository = SyncJobRepository()
