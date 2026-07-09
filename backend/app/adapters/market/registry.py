from __future__ import annotations

from app.adapters.market.amazon_market_adapter import AmazonMarketAdapter
from app.adapters.market.base import MarketAdapterBase
from app.adapters.market.google_trends_adapter import GoogleTrendsAdapter
from app.adapters.market.shopify_market_adapter import ShopifyMarketAdapter
from app.adapters.market.tiktok_market_adapter import TikTokMarketAdapter


class MarketAdapterRegistry:
    def __init__(self):
        self._adapters: list[MarketAdapterBase] | None = None

    def _get_adapters(self) -> list[MarketAdapterBase]:
        if self._adapters is None:
            self._adapters = [
                GoogleTrendsAdapter(),
                AmazonMarketAdapter(),
                ShopifyMarketAdapter(),
                TikTokMarketAdapter(),
            ]
        return self._adapters

    def resolve(self, market: str) -> MarketAdapterBase:
        normalized = market.strip().lower()
        adapters = self._get_adapters()
        if normalized == "shopify":
            return next(item for item in adapters if isinstance(item, ShopifyMarketAdapter))
        if normalized == "amazon":
            return next(item for item in adapters if isinstance(item, AmazonMarketAdapter))
        if normalized == "tiktok":
            return next(item for item in adapters if isinstance(item, TikTokMarketAdapter))
        return GoogleTrendsAdapter()


market_adapter_registry = MarketAdapterRegistry()
