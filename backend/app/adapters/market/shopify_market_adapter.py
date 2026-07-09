from __future__ import annotations

from statistics import mean

from app.adapters.market.market_base import MarketDataAdapter
from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter


class ShopifyMarketAdapter(MarketDataAdapter):
    source_name = "shopify_market"

    def __init__(self) -> None:
        self.shopify = ShopifyPlatformAdapter()

    async def fetch(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> dict:
        del region, category
        products = self.shopify.search_product(keyword)
        if not products or (products and products[0].get("error")):
            detail = products[0].get("error") if products else "SHOPIFY_MARKET_EMPTY"
            return self._envelope(
                source=f"{self.source_name}_mock",
                data={
                    "category_activity": 26.0,
                    "store_count_signal": 0,
                    "product_count": 0,
                    "category_count": 0,
                    "active_products": 0,
                    "active_product_ratio": 0.0,
                    "price_range": {"min": 0.0, "max": 0.0},
                    "growth_signal": 24.0,
                    "fallback_reason": detail,
                },
                confidence=0.2,
                is_mock=True,
                source_status="pending",
            )

        prices = [float(item.get("price") or 0) for item in products if str(item.get("price") or "").strip()]
        inventory = [int(item.get("inventory_quantity") or 0) for item in products]
        active_products = sum(1 for qty in inventory if qty > 0)
        category_labels = {str(item.get("product_type") or item.get("vendor") or "").strip() for item in products if str(item.get("product_type") or item.get("vendor") or "").strip()}
        category_activity = min(100.0, round(25 + len(products) * 12, 2))
        growth_signal = min(
            100.0,
            round(
                20
                + (active_products * 8)
                + (mean(prices) / 5 if prices else 0),
                2,
            ),
        )
        return self._envelope(
            source=f"{self.source_name}_real",
            data={
                "category_activity": category_activity,
                "store_count_signal": len(products),
                "product_count": len(products),
                "category_count": len(category_labels),
                "active_products": active_products,
                "active_product_ratio": round((active_products / len(products)), 4) if products else 0.0,
                "price_range": {
                    "min": round(min(prices), 2) if prices else 0.0,
                    "max": round(max(prices), 2) if prices else 0.0,
                },
                "growth_signal": growth_signal,
            },
            confidence=0.76,
            is_mock=False,
            source_status="real",
        )
