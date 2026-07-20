from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class DataSourceRegistryRecord(TimestampMixin, Base):
    __tablename__ = "data_source_registry"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="success")


class SyncJobRecord(TimestampMixin, Base):
    __tablename__ = "sync_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    workspace_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    api_key_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    job_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    platform: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_payload: Mapped[dict | None] = mapped_column(json_field, nullable=True)


class DataLineageRecord(Base):
    __tablename__ = "data_lineage_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    event_key: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    event_stage: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    workspace_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    task_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    api_key_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True, default="trace")
    lineage_chain: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
    transform_steps: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
    payload_json: Mapped[dict | None] = mapped_column(json_field, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)


class DataQualityHistory(TimestampMixin, Base):
    __tablename__ = "data_quality_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    data_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    truth_level: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence_score: Mapped[float] = mapped_column(nullable=False)
    freshness_score: Mapped[float] = mapped_column(nullable=False)
    reliability_score: Mapped[float] = mapped_column(nullable=False)
