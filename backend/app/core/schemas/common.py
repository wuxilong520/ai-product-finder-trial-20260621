from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


SourceType = Literal["mock", "api", "estimated", "imported"]
TruthLevel = Literal["real", "semi_real", "simulated"]
SyncStatus = Literal["success", "pending", "failed"]


class DataSourceMeta(BaseModel):
    source_type: SourceType = "mock"
    source_id: str | None = None
    workspace_id: int | None = None
    user_id: int | None = None
    api_key_id: int | None = None
    truth_level: TruthLevel = "simulated"
    confidence_score: float = Field(default=0.3, ge=0.0, le=1.0)
    freshness_score: float = Field(default=0.3, ge=0.0, le=1.0)
    sync_status: SyncStatus = "success"
    last_verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lineage_chain: list[str] = Field(default_factory=list)


class TimestampedSchema(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseDataSchema(TimestampedSchema, DataSourceMeta):
    provider_name: str | None = None
    fetch_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transform_steps: list[str] = Field(default_factory=list)
