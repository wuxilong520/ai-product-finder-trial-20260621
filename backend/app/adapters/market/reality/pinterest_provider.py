from __future__ import annotations

from importlib import import_module


GlobalMarketProvider = import_module("app.adapters.market.global.global_market_base").GlobalMarketProvider


class PinterestRealityProvider(GlobalMarketProvider):
    source_name = "pinterest"
    signal_type = "content"

    async def fetch_signal(self, keyword: str, country: str):
        return self.build_signal(
            keyword=keyword,
            country=country,
            value=0,
            trend="flat",
            confidence=0.25,
            data_status="limited",
            metrics={
                "status": "limited",
                "reason": "Pinterest free production API not configured",
            },
        )
