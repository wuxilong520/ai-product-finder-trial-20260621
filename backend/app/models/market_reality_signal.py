from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MarketRealitySignal(BaseModel):
    source_name: str
    signal_type: str
    value: float = Field(default=0.0, ge=0, le=100)
    reliability: float = Field(default=0.0, ge=0, le=1)
    timestamp: str = ""
    is_real: bool = False
    status: str = "fallback"
    metadata: dict[str, Any] = Field(default_factory=dict)
