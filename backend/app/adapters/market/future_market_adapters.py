from __future__ import annotations

from app.adapters.market.base import MarketAdapterBase
from app.core.contracts import MarketInsight, TrendPoint


class AmazonMarketAdapter(MarketAdapterBase):
    adapter_name = "amazon_market_placeholder"
    supported_channels = ("amazon",)

    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        return MarketInsight(
            source=self.adapter_name,
            keyword=keyword,
            market=market,
            trend_direction="flat",
            demand_score=60,
            competition_score=62,
            trend_points=[TrendPoint(date="2026-06-29", score=60)],
            summary="这是为未来 Amazon 真实接入预留的占位适配器。",
        )


class ShopeeMarketAdapter(MarketAdapterBase):
    adapter_name = "shopee_market_placeholder"
    supported_channels = ("shopee",)

    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        return MarketInsight(
            source=self.adapter_name,
            keyword=keyword,
            market=market,
            trend_direction="flat",
            demand_score=58,
            competition_score=54,
            trend_points=[TrendPoint(date="2026-06-29", score=58)],
            summary="这是为未来 Shopee 真实接入预留的占位适配器。",
        )


class TikTokMarketAdapter(MarketAdapterBase):
    adapter_name = "tiktok_market_placeholder"
    supported_channels = ("tiktok",)

    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        return MarketInsight(
            source=self.adapter_name,
            keyword=keyword,
            market=market,
            trend_direction="up",
            demand_score=66,
            competition_score=49,
            trend_points=[TrendPoint(date="2026-06-29", score=66)],
            summary="这是为未来 TikTok Shop 真实接入预留的占位适配器。",
        )
