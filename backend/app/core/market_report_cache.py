from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any


@dataclass
class CacheEntry:
    expires_at: datetime
    payload: dict[str, Any]


class MarketReportCache:
    def __init__(self, ttl_minutes: int = 30) -> None:
        self.ttl = timedelta(minutes=ttl_minutes)
        self._store: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def build_key(
        self,
        *,
        report_type: str,
        keyword: str,
        region: str,
        category: str | None = None,
        user_id: int | None = None,
    ) -> str:
        normalized_keyword = keyword.strip().lower()
        normalized_region = (region or "US").strip().upper()
        normalized_category = (category or "").strip().lower()
        normalized_user = str(user_id or 0)
        return f"{report_type}|{normalized_keyword}|{normalized_region}|{normalized_category}|{normalized_user}"

    def get(self, key: str) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if entry.expires_at <= now:
                self._store.pop(key, None)
                return None
            return dict(entry.payload)

    def set(self, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._store[key] = CacheEntry(
                expires_at=datetime.now(timezone.utc) + self.ttl,
                payload=dict(payload),
            )
        return dict(payload)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


market_report_cache = MarketReportCache()
