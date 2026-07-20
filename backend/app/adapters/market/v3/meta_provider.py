from __future__ import annotations

import httpx

from app.adapters.market.v3 import MarketDataProvider, MarketSignal
from app.core.config import settings


class MetaMarketProvider(MarketDataProvider):
    provider_name = "meta"

    async def fetch_signal(
        self,
        *,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> MarketSignal:
        del category
        if not str(settings.meta_access_token or "").strip():
            return self._config_required(
                keyword=keyword,
                region=region,
                missing_credentials=["META_ACCESS_TOKEN"],
                error_detail="Meta Ads Library API 需要 access token",
            )
        try:
            params = {
                "search_terms": keyword,
                "ad_reached_countries": [str(region or "US").upper()],
                "fields": "id,page_name,ad_creation_time,ad_delivery_start_time",
                "access_token": str(settings.meta_access_token or "").strip(),
                "limit": 50,
            }
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get("https://graph.facebook.com/v25.0/ads_archive", params=params)
                response.raise_for_status()
                data = response.json() or {}
            ads = list(data.get("data") or [])
            competition = min(100.0, len(ads) * 2.0)
            interest = min(100.0, 10 + len(ads) * 1.2)
            value = max(0.0, min(100.0, interest - competition * 0.25 + 20))
            advertisers = {str(item.get("page_name") or "").strip() for item in ads if str(item.get("page_name") or "").strip()}
            return self._signal(
                keyword=keyword,
                region=region,
                value=value,
                confidence=0.78,
                is_real=True,
                api_status="REAL",
                metrics={
                    "advertiser_count": len(advertisers),
                    "ad_count": len(ads),
                    "ad_velocity": round(len(ads) / 7.0, 2) if ads else 0.0,
                    "ad_competition": round(competition, 2),
                    "competition_score": round(competition, 2),
                    "consumer_interest": round(interest, 2),
                },
            )
        except Exception as exc:
            return self._unavailable(keyword=keyword, region=region, error_detail=f"Meta Ads Library 失败: {exc}")
