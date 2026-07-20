from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class MarketSignal(BaseModel):
    source: str
    keyword: str
    region: str
    timestamp: str
    value: float = Field(default=0.0, ge=0, le=100)
    confidence: float = Field(default=0.0, ge=0, le=1)
    is_real: bool = False
    api_status: str = "UNAVAILABLE"
    metrics: dict[str, Any] = Field(default_factory=dict)
    missing_credentials: list[str] = Field(default_factory=list)
    error_detail: str = ""


class MarketProvider(ABC):
    provider_name: str = ""

    @abstractmethod
    async def fetch_signal(
        self,
        *,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> MarketSignal:
        raise NotImplementedError

    def _signal(
        self,
        *,
        keyword: str,
        region: str,
        value: float,
        confidence: float,
        is_real: bool,
        api_status: str,
        metrics: dict[str, Any] | None = None,
        missing_credentials: list[str] | None = None,
        error_detail: str = "",
    ) -> MarketSignal:
        return MarketSignal(
            source=self.provider_name,
            keyword=keyword,
            region=region,
            timestamp=datetime.now(UTC).isoformat(),
            value=max(0.0, min(100.0, round(float(value or 0), 2))),
            confidence=max(0.0, min(1.0, round(float(confidence or 0), 4))),
            is_real=is_real,
            api_status=api_status,
            metrics=metrics or {},
            missing_credentials=missing_credentials or [],
            error_detail=error_detail,
        )

    def _config_required(
        self,
        *,
        keyword: str,
        region: str,
        missing_credentials: list[str],
        error_detail: str = "",
    ) -> MarketSignal:
        return self._signal(
            keyword=keyword,
            region=region,
            value=0.0,
            confidence=0.0,
            is_real=False,
            api_status="CONFIG_REQUIRED",
            missing_credentials=missing_credentials,
            error_detail=error_detail or "缺少真实 API 配置",
        )

    def _unavailable(
        self,
        *,
        keyword: str,
        region: str,
        error_detail: str,
        metrics: dict[str, Any] | None = None,
    ) -> MarketSignal:
        return self._signal(
            keyword=keyword,
            region=region,
            value=0.0,
            confidence=0.0,
            is_real=False,
            api_status="UNAVAILABLE",
            metrics=metrics,
            error_detail=error_detail,
        )
