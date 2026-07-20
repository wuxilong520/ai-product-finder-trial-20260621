from __future__ import annotations

from statistics import mean

from app.adapters.execution.shopify_adapter import ShopifyExecutionAdapter
from app.adapters.market.v3 import MarketDataProvider, MarketSignal
from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter
from app.core.config import settings


class ShopifyMarketProviderV3(MarketDataProvider):
    provider_name = "shopify"

    def __init__(self) -> None:
        self.platform_adapter = ShopifyPlatformAdapter()
        self.execution_adapter = ShopifyExecutionAdapter()

    async def fetch_signal(
        self,
        *,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> MarketSignal:
        del category
        missing = []
        if not str(settings.shopify_store_base_url or "").strip():
            missing.append("SHOPIFY_STORE_BASE_URL")
        if not str(settings.shopify_api_key or "").strip():
            missing.append("SHOPIFY_API_KEY")
        if not str(settings.shopify_api_secret or "").strip():
            missing.append("SHOPIFY_API_SECRET")
        if missing:
            return self._config_required(
                keyword=keyword,
                region=region,
                missing_credentials=missing,
                error_detail="Shopify 市场层需要读取真实店铺商品数据",
            )

        try:
            products = self.platform_adapter.search_product(keyword)
            if products and isinstance(products, list) and products[0].get("error"):
                return self._unavailable(
                    keyword=keyword,
                    region=region,
                    error_detail=str(products[0].get("detail") or products[0].get("error")),
                )
            product_list = list(products or [])
            price_values = [float(item.get("price") or 0) for item in product_list if str(item.get("price") or "").strip()]
            category_activity = min(100.0, 20 + len(product_list) * 10)
            selling_signal = min(
                100.0,
                (sum(price_values) / max(len(price_values), 1)) if price_values else category_activity * 0.65,
            )
            order_metrics = {
                "orders": 0,
                "analytics": {
                    "avg_order_value": 0.0,
                    "refund_rate": 0.0,
                },
            }
            confidence = 0.78
            api_status = "REAL"
            try:
                orders_payload = self.execution_adapter.fetch_orders(limit=50)
                if not orders_payload.get("error"):
                    orders = list(orders_payload.get("orders") or [])
                    selling_signal = min(100.0, len(orders) * 2 + sum(float(item.get("total_price") or 0) for item in orders) / 100.0)
                    order_metrics = {
                        "orders": len(orders),
                        "analytics": {
                            "avg_order_value": round(mean([float(item.get("total_price") or 0) for item in orders]), 2) if orders else 0.0,
                            "refund_rate": round(
                                sum(float(item.get("refund_total") or 0) for item in orders) / max(sum(float(item.get("total_price") or 0) for item in orders), 1.0),
                                4,
                            ) if orders else 0.0,
                        },
                    }
                    confidence = 0.86
                else:
                    api_status = "PARTIAL_REAL"
            except Exception:
                api_status = "PARTIAL_REAL"

            value = min(100.0, category_activity * 0.55 + selling_signal * 0.45)
            return self._signal(
                keyword=keyword,
                region=region,
                value=value,
                confidence=confidence,
                is_real=True,
                api_status=api_status,
                metrics={
                    "products": len(product_list),
                    **order_metrics,
                    "store_activity": round(category_activity, 2),
                    "category_activity": round(category_activity, 2),
                    "category_growth": round(max(0.0, category_activity - 20.0), 2),
                    "selling_signal": round(selling_signal, 2),
                    "price_range": {
                        "min": round(min(price_values), 2) if price_values else 0.0,
                        "max": round(max(price_values), 2) if price_values else 0.0,
                        "average": round(mean(price_values), 2) if price_values else 0.0,
                    },
                    "price_band": {
                        "min": round(min(price_values), 2) if price_values else 0.0,
                        "max": round(max(price_values), 2) if price_values else 0.0,
                        "average": round(mean(price_values), 2) if price_values else 0.0,
                    },
                },
            )
        except Exception as exc:
            return self._unavailable(keyword=keyword, region=region, error_detail=f"Shopify provider 失败: {exc}")
