from sqlalchemy import select
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.data_governance import DataLineageRecord, DataQualityHistory, DataSourceRegistryRecord, SyncJobRecord


class DataSourceRegistryRepository:
    def create(self, db: Session, *, source_type: str, provider_name: str, status: str, workspace_id: int | None = None) -> DataSourceRegistryRecord:
        record = DataSourceRegistryRecord(
            workspace_id=workspace_id,
            source_type=source_type,
            provider_name=provider_name,
            status=status,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


class DataLineageRepository:
    def get_by_event_key(self, db: Session, event_key: str) -> DataLineageRecord | None:
        stmt = select(DataLineageRecord).where(DataLineageRecord.event_key == event_key)
        return db.scalar(stmt)

    def update_existing(
        self,
        db: Session,
        record: DataLineageRecord,
        *,
        workspace_id: int | None = None,
        task_id: int | None = None,
        user_id: int | None = None,
        api_key_id: int | None = None,
        source_id: str | None = None,
        provider_name: str | None = None,
        node_type: str | None = None,
        lineage_chain: list[str] | None = None,
        transform_steps: list[str] | None = None,
        payload_json: dict | None = None,
    ) -> DataLineageRecord:
        record.workspace_id = workspace_id if workspace_id is not None else record.workspace_id
        record.task_id = task_id if task_id is not None else record.task_id
        record.user_id = user_id if user_id is not None else record.user_id
        record.api_key_id = api_key_id if api_key_id is not None else record.api_key_id
        record.source_id = source_id or record.source_id
        record.provider_name = provider_name or record.provider_name
        record.node_type = node_type or record.node_type
        if lineage_chain:
            record.lineage_chain = lineage_chain
        if transform_steps:
            record.transform_steps = transform_steps
        if payload_json:
            record.payload_json = payload_json
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def create(
        self,
        db: Session,
        *,
        event_id: str | None = None,
        event_key: str | None = None,
        event_stage: str | None = None,
        workspace_id: int | None = None,
        task_id: int | None = None,
        user_id: int | None = None,
        api_key_id: int | None = None,
        source_id: str,
        provider_name: str,
        node_type: str = "legacy",
        lineage_chain: list[str],
        transform_steps: list[str],
        payload_json: dict | None = None,
        created_at: str,
    ) -> DataLineageRecord:
        record = DataLineageRecord(
            event_id=event_id,
            event_key=event_key,
            event_stage=event_stage,
            workspace_id=workspace_id,
            task_id=task_id,
            user_id=user_id,
            api_key_id=api_key_id,
            source_id=source_id,
            provider_name=provider_name,
            node_type=node_type,
            lineage_chain=lineage_chain,
            transform_steps=transform_steps,
            payload_json=payload_json,
            created_at=created_at,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


class DataQualityHistoryRepository:
    def create(
        self,
        db: Session,
        *,
        workspace_id: int | None = None,
        data_id: str,
        truth_level: str,
        confidence_score: float,
        freshness_score: float,
        reliability_score: float,
    ) -> DataQualityHistory:
        record = DataQualityHistory(
            workspace_id=workspace_id,
            data_id=data_id,
            truth_level=truth_level,
            confidence_score=confidence_score,
            freshness_score=freshness_score,
            reliability_score=reliability_score,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


class SyncJobRepository:
    def create(
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
    ) -> SyncJobRecord:
        record = SyncJobRecord(
            user_id=user_id,
            workspace_id=workspace_id,
            api_key_id=api_key_id,
            job_type=job_type,
            status=status,
            retry_count=retry_count,
            last_error=last_error,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_by_id(self, db: Session, record_id: int) -> SyncJobRecord | None:
        return db.get(SyncJobRecord, record_id)

    def update_status(
        self,
        db: Session,
        record_id: int,
        *,
        status: str,
        retry_count: int | None = None,
        last_error: str | None = None,
        result_payload: dict | None = None,
    ) -> SyncJobRecord | None:
        record = db.get(SyncJobRecord, record_id)
        if not record:
            return None
        record.status = status
        if retry_count is not None:
            record.retry_count = retry_count
        record.last_error = last_error
        if result_payload is not None:
            record.result_payload = result_payload
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_recent(self, db: Session, limit: int = 50, workspace_id: int | None = None) -> list[SyncJobRecord]:
        stmt = select(SyncJobRecord)
        if workspace_id is not None:
            stmt = stmt.where(SyncJobRecord.workspace_id == workspace_id)
        stmt = stmt.order_by(SyncJobRecord.updated_at.desc()).limit(limit)
        return list(db.scalars(stmt))

    def list_all(self, db: Session, limit: int = 200, workspace_id: int | None = None) -> list[SyncJobRecord]:
        stmt = select(SyncJobRecord)
        if workspace_id is not None:
            stmt = stmt.where(SyncJobRecord.workspace_id == workspace_id)
        stmt = stmt.order_by(desc(SyncJobRecord.id)).limit(limit)
        return list(db.scalars(stmt))


data_source_registry_repository = DataSourceRegistryRepository()
data_lineage_repository = DataLineageRepository()
data_quality_history_repository = DataQualityHistoryRepository()
sync_job_repository = SyncJobRepository()
