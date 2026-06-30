from __future__ import annotations

from datetime import datetime, timezone


class DataTraceabilitySystem:
    def build_trace(
        self,
        *,
        source_id: str,
        source_type: str,
        provider_name: str,
        transform_steps: list[str] | None = None,
        lineage_chain: list[str] | None = None,
    ) -> dict:
        fetch_timestamp = datetime.now(timezone.utc)
        return {
            "source_id": source_id,
            "source_type": source_type,
            "provider_name": provider_name,
            "fetch_timestamp": fetch_timestamp,
            "transform_steps": transform_steps or [],
            "lineage_chain": lineage_chain or [provider_name, "pipeline", "data_hub"],
            "last_verified_at": fetch_timestamp,
        }


data_traceability_system = DataTraceabilitySystem()
