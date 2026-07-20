from __future__ import annotations

import httpx

from app.adapters.market.v3 import MarketDataProvider, MarketSignal
from app.core.config import settings


class PinterestMarketProvider(MarketDataProvider):
    provider_name = "pinterest"

    async def fetch_signal(
        self,
        *,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> MarketSignal:
        del category
        if not str(settings.pinterest_access_token or "").strip():
            return self._config_required(
                keyword=keyword,
                region=region,
                missing_credentials=["PINTEREST_ACCESS_TOKEN"],
                error_detail="Pinterest Trends 需要 access token",
            )
        try:
            headers = {"Authorization": f"Bearer {settings.pinterest_access_token}"}
            params = {
                "region": str(region or "US").upper(),
                "trend_type": "growing",
                "limit": 50,
            }
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get("https://api.pinterest.com/v5/trends/keywords", headers=headers, params=params)
                response.raise_for_status()
                rows = list((response.json() or {}).get("trends") or (response.json() or {}).get("items") or [])
            matched = [item for item in rows if keyword.lower() in str(item).lower()]
            interest = min(100.0, len(matched) * 18 + 15)
            return self._signal(
                keyword=keyword,
                region=region,
                value=interest,
                confidence=0.8 if matched else 0.55,
                is_real=True,
                api_status="REAL",
                metrics={
                    "matched_keywords": len(matched),
                    "consumer_interest": round(interest, 2),
                },
            )
        except Exception as exc:
            return self._unavailable(keyword=keyword, region=region, error_detail=f"Pinterest Trends 失败: {exc}")
