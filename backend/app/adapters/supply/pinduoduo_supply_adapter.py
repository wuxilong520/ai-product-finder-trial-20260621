from __future__ import annotations

from app.adapters.supply.supply_base import SupplyDataAdapter


class PinduoduoSupplyAdapter(SupplyDataAdapter):
    source_name = "pinduoduo_supply"

    async def fetch(
        self,
        keyword: str,
        target_market: str,
        category: str | None = None,
        expected_price: float | None = None,
        quantity: int = 100,
    ) -> dict:
        del target_market, category, expected_price, quantity
        return self._envelope(
            source=f"{self.source_name}_pending",
            data={
                "keyword": keyword,
                "suppliers": [],
                "platform": "pinduoduo",
                "message": "拼多多供应链接口当前只预留结构，未接入真实数据。",
                "data_source": "mock",
            },
            confidence=0.1,
            is_mock=True,
            source_status="pending",
        )
