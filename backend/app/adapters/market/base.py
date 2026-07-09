from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from app.adapters.market.market_base import MarketDataAdapter as MarketAdapterBase


class MarketProvider(ABC):
    provider_name: str = ""

    @abstractmethod
    async def fetch_market_signal(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
        time_range: str = "90d",
    ) -> dict[str, Any]:
        raise NotImplementedError

    def _signal_envelope(
        self,
        *,
        source: str,
        source_status: str,
        signal: dict[str, Any],
        confidence: float,
        is_mock: bool = False,
    ) -> dict[str, Any]:
        return {
            "source": source,
            "source_status": source_status,
            "signal": signal,
            "timestamp": datetime.now(UTC).isoformat(),
            "confidence": round(max(0.0, min(1.0, float(confidence))), 4),
            "is_mock": bool(is_mock),
        }
