from __future__ import annotations

from statistics import mean

from app.adapters.market.base import MarketProvider
from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter


class ShopifyMarketProvider(MarketProvider):
    provider_name = "shopify"

    def __init__(self) -> None:
        self.shopify = ShopifyPlatformAdapter()

    async def fetch_market_signal(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
        time_range: str = "90d",
    ) -> dict:
        del region, category, time_range
        products = self.shopify.search_product(keyword)
        if not products or (products and products[0].get("error")):
            reason = products[0].get("error") if products else "SHOPIFY_MARKET_EMPTY"
            return self._signal_envelope(
                source=self.provider_name,
                source_status="unavailable",
                confidence=0.0,
                signal={
                    "category_activity": 0.0,
                    "store_density": 0.0,
                    "product_frequency": 0.0,
                    "price_range": {"min": 0.0, "max": 0.0, "average": 0.0},
                    "market_growth": 0.0,
                    "data_scope": "user_store",
                    "reason": reason,
                },
            )

        prices = [float(item.get("price") or 0) for item in products if str(item.get("price") or "").strip()]
        inventory = [int(item.get("inventory_quantity") or 0) for item in products]
        active_products = sum(1 for qty in inventory if qty > 0)
        average_price = round(mean(prices), 2) if prices else 0.0
        market_growth = round(min(100.0, 15 + active_products * 8 + (average_price / 4 if average_price else 0)), 2)
        return self._signal_envelope(
            source=self.provider_name,
            source_status="partial",
            confidence=0.52,
            signal={
                "category_activity": round(min(100.0, 20 + len(products) * 10), 2),
                "store_density": round(min(100.0, len(products) * 6), 2),
                "product_frequency": round(min(100.0, active_products * 10), 2),
                "price_range": {
                    "min": round(min(prices), 2) if prices else 0.0,
                    "max": round(max(prices), 2) if prices else 0.0,
                    "average": average_price,
                },
                "market_growth": market_growth,
                "data_scope": "user_store",
            },
        )
