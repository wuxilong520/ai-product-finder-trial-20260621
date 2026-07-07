from __future__ import annotations

from app.adapters.market.base import MarketAdapterBase
from app.core.contracts import MarketInsight, TrendPoint


class AmazonMarketAdapter(MarketAdapterBase):
    adapter_name = "amazon_market_mock"
    supported_channels = ("amazon",)

    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        return MarketInsight(
            source=self.adapter_name,
            keyword=keyword,
            market=market,
            trend_direction="up",
            demand_score=68,
            competition_score=64,
            trend_points=[
                TrendPoint(date="2026-06-01", score=57),
                TrendPoint(date="2026-06-08", score=61),
                TrendPoint(date="2026-06-15", score=65),
                TrendPoint(date="2026-06-22", score=68),
                TrendPoint(date="2026-06-29", score=70),
            ],
            summary=f"{keyword} 在 Amazon 搜索场景里有基础需求，但竞争不低，适合先测试。",
        )
