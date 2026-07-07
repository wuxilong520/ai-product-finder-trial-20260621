from __future__ import annotations

from app.adapters.market.base import MarketAdapterBase
from app.core.contracts import MarketInsight, TrendPoint


class TikTokTrendsAdapter(MarketAdapterBase):
    adapter_name = "tiktok_trends_mock"
    supported_channels = ("tiktok",)

    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        return MarketInsight(
            source=self.adapter_name,
            keyword=keyword,
            market=market,
            trend_direction="up",
            demand_score=72,
            competition_score=48,
            trend_points=[
                TrendPoint(date="2026-06-01", score=50),
                TrendPoint(date="2026-06-08", score=58),
                TrendPoint(date="2026-06-15", score=63),
                TrendPoint(date="2026-06-22", score=71),
                TrendPoint(date="2026-06-29", score=78),
            ],
            summary=f"{keyword} 在 TikTok 趋势信号里有放量迹象，适合关注内容传播机会。",
        )
