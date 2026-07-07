from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.contracts import MarketInsight


class MarketAdapterBase(ABC):
    adapter_name: str
    supported_channels: tuple[str, ...]

    @abstractmethod
    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        raise NotImplementedError
