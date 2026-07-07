from __future__ import annotations

from app.adapters.market.base import MarketAdapterBase
from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter
from app.core.contracts import MarketInsight, TrendPoint


class ShopifyCategoryAdapter(MarketAdapterBase):
    adapter_name = "shopify_category_partial"
    supported_channels = ("shopify",)

    def __init__(self) -> None:
        self.shopify = ShopifyPlatformAdapter()

    def fetch_market_insight(self, *, keyword: str, market: str) -> MarketInsight:
        candidates = self.shopify.search_product(keyword)
        if candidates and not candidates[0].get("error"):
            demand_score = min(85, 40 + (len(candidates) * 18))
            competition_score = min(90, 28 + (len(candidates) * 15))
            trend_points = [
                TrendPoint(date="2026-06-01", score=max(35, demand_score - 18)),
                TrendPoint(date="2026-06-08", score=max(38, demand_score - 12)),
                TrendPoint(date="2026-06-15", score=max(42, demand_score - 8)),
                TrendPoint(date="2026-06-22", score=max(45, demand_score - 4)),
                TrendPoint(date="2026-06-29", score=demand_score),
            ]
            return MarketInsight(
                source=self.adapter_name,
                keyword=keyword,
                market=market,
                trend_direction="up" if demand_score >= 55 else "flat",
                demand_score=int(demand_score),
                competition_score=int(competition_score),
                trend_points=trend_points,
                summary=f"{keyword} 在当前 Shopify 店铺样本里已检出 {len(candidates)} 个商品记录。",
            )

        return MarketInsight(
            source="shopify_category_mock",
            keyword=keyword,
            market=market,
            trend_direction="flat",
            demand_score=45,
            competition_score=42,
            trend_points=[TrendPoint(date="2026-06-29", score=45)],
            summary=f"{keyword} 当前没有足够的 Shopify 类目样本，先按保守占位逻辑输出。",
        )
