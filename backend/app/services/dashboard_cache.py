from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import monotonic
from typing import Any


@dataclass
class CacheEntry:
    expires_at: float
    value: Any
    generated_at: datetime


class DashboardCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if not entry:
            return None
        if monotonic() >= entry.expires_at:
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> Any:
        self._store[key] = CacheEntry(
            expires_at=monotonic() + ttl_seconds,
            value=value,
            generated_at=datetime.now(UTC),
        )
        return value

    def get_or_set(self, key: str, ttl_seconds: int, factory) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = factory()
        return self.set(key, value, ttl_seconds)

    def clear(self, key: str | None = None) -> None:
        if key is None:
            self._store.clear()
            return
        self._store.pop(key, None)


dashboard_cache = DashboardCache()

