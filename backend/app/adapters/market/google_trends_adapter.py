from __future__ import annotations

from app.adapters.market.base import MarketAdapterBase
from app.core.contracts import MarketInsight, TrendPoint


class GoogleTrendsAdapter(MarketAdapterBase):
    adapter_name = "google_trends_mock"
    supported_channels = ("amazon", "shopify", "shopee", "tiktok")

    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        points = [
            TrendPoint(date="2026-06-01", score=52),
            TrendPoint(date="2026-06-08", score=58),
            TrendPoint(date="2026-06-15", score=64),
            TrendPoint(date="2026-06-22", score=71),
            TrendPoint(date="2026-06-29", score=76),
        ]
        return MarketInsight(
            source=self.adapter_name,
            keyword=keyword,
            market=market,
            trend_direction="up",
            demand_score=76,
            competition_score=57,
            trend_points=points,
            summary=f"{keyword} 在最近 30 天呈上升趋势，适合先进入小范围验证。",
        )
