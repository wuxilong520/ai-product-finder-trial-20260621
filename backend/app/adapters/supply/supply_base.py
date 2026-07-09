from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any


class SupplyDataAdapter(ABC):
    source_name: str = ""

    @abstractmethod
    async def fetch(
        self,
        keyword: str,
        target_market: str,
        category: str | None = None,
        expected_price: float | None = None,
        quantity: int = 100,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def _envelope(
        self,
        *,
        source: str,
        data: dict[str, Any],
        confidence: float,
        is_mock: bool,
        source_status: str,
    ) -> dict[str, Any]:
        return {
            "source": source,
            "data": data,
            "timestamp": datetime.now(UTC).isoformat(),
            "confidence": round(max(0.0, min(1.0, float(confidence))), 4),
            "is_mock": bool(is_mock),
            "source_status": source_status,
        }
