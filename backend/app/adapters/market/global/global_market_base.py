from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MarketSignal(BaseModel):
    source: str
    keyword: str
    country: str
    signal_type: str
    value: float = Field(default=0.0, ge=0, le=100)
    trend: str = "flat"
    timestamp: str
    confidence: float = Field(default=0.0, ge=0, le=1)
    is_mock: bool = False
    data_status: str = "fallback"
    metrics: dict[str, Any] = Field(default_factory=dict)
    error_detail: str = ""


class GlobalMarketProvider(ABC):
    source_name: str = ""
    signal_type: str = "trend"

    @abstractmethod
    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        raise NotImplementedError

    def build_signal(
        self,
        *,
        keyword: str,
        country: str,
        value: float,
        trend: str,
        confidence: float,
        data_status: str,
        metrics: dict[str, Any] | None = None,
        error_detail: str = "",
        is_mock: bool = False,
    ) -> MarketSignal:
        return MarketSignal(
            source=self.source_name,
            keyword=keyword,
            country=country,
            signal_type=self.signal_type,
            value=max(0.0, min(100.0, round(float(value or 0), 2))),
            trend=str(trend or "flat"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=max(0.0, min(1.0, round(float(confidence or 0), 4))),
            is_mock=is_mock,
            data_status=data_status,
            metrics=metrics or {},
            error_detail=error_detail,
        )
