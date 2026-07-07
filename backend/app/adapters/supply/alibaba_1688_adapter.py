from __future__ import annotations

from app.adapters.supply.base import SupplyAdapterBase
from app.core.contracts import SupplyOffer


class Alibaba1688Adapter(SupplyAdapterBase):
    adapter_name = "1688_mock"
    supported_channels = ("amazon", "shopify", "shopee", "tiktok", "1688")

    def search_supply(self, *, keyword: str, market: str) -> list[SupplyOffer]:
        return [
            SupplyOffer(
                source=self.adapter_name,
                supplier_id="1688-A1001",
                supplier_name="义乌优选工厂",
                keyword=keyword,
                product_title=f"{keyword} 基础款",
                price=16.8,
                min_order_qty=50,
                rating=4.7,
                shipping_days=6,
            ),
            SupplyOffer(
                source=self.adapter_name,
                supplier_id="1688-A1002",
                supplier_name="杭州稳定供货商",
                keyword=keyword,
                product_title=f"{keyword} 升级款",
                price=19.5,
                min_order_qty=30,
                rating=4.9,
                shipping_days=4,
            ),
            SupplyOffer(
                source=self.adapter_name,
                supplier_id="1688-A1003",
                supplier_name="深圳快速打样供应商",
                keyword=keyword,
                product_title=f"{keyword} 试卖款",
                price=14.2,
                min_order_qty=80,
                rating=4.4,
                shipping_days=7,
            ),
        ]
