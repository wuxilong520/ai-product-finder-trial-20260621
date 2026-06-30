from __future__ import annotations

from datetime import datetime, timezone


class DataSourceRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, dict] = {}

    def register_source(
        self,
        *,
        source_id: str,
        source_type: str,
        provider_name: str,
        status: str = "success",
        meta: dict | None = None,
    ) -> dict:
        payload = {
            "source_id": source_id,
            "source_type": source_type,
            "provider_name": provider_name,
            "status": status,
            "meta": meta or {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._sources[source_id] = payload
        return payload

    def get_source(self, source_id: str) -> dict | None:
        return self._sources.get(source_id)

    def list_sources(self) -> list[dict]:
        return list(self._sources.values())

    def update_source_status(self, source_id: str, status: str) -> dict | None:
        source = self._sources.get(source_id)
        if not source:
            return None
        source["status"] = status
        source["updated_at"] = datetime.now(timezone.utc).isoformat()
        return source


data_source_registry = DataSourceRegistry()
