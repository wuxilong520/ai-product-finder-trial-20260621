from __future__ import annotations

from app.adapters.market.base import MarketAdapterBase
from app.adapters.market.future_market_adapters import AmazonMarketAdapter, ShopeeMarketAdapter, TikTokMarketAdapter
from app.adapters.market.google_trends_adapter import GoogleTrendsAdapter


class MarketAdapterRegistry:
    def __init__(self):
        self._adapters: list[MarketAdapterBase] = [
            GoogleTrendsAdapter(),
            AmazonMarketAdapter(),
            ShopeeMarketAdapter(),
            TikTokMarketAdapter(),
        ]

    def resolve(self, market: str) -> MarketAdapterBase:
        normalized = market.strip().lower()
        for adapter in self._adapters:
            if normalized in adapter.supported_channels:
                if adapter.adapter_name == "google_trends_mock":
                    return adapter
        for adapter in self._adapters:
            if normalized in adapter.supported_channels:
                return adapter
        return GoogleTrendsAdapter()


market_adapter_registry = MarketAdapterRegistry()
