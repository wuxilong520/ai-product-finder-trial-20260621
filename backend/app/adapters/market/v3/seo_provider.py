from __future__ import annotations

from statistics import mean

import httpx

from app.adapters.market.v3 import MarketDataProvider, MarketSignal
from app.core.config import settings


class SeoMarketProviderV3(MarketDataProvider):
    provider_name = "seo"

    async def fetch_signal(
        self,
        *,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> MarketSignal:
        del category
        missing = self._missing_credentials()
        if missing:
            return self._config_required(
                keyword=keyword,
                region=region,
                missing_credentials=missing,
                error_detail="SEO 真实层需要 DataForSEO 或 Bing Webmaster 凭证",
            )
        try:
            metrics = await self._fetch_dataforseo(keyword=keyword, region=region)
            search_volume = float(metrics.get("search_volume") or 0)
            cpc = float(metrics.get("cpc") or 0)
            competition = float(metrics.get("competition") or 0)
            keyword_growth = float(metrics.get("keyword_growth") or 0)
            value = max(
                0.0,
                min(
                    100.0,
                    min(search_volume / 100.0, 60.0) * 0.55
                    + min(cpc * 5.0, 15.0)
                    + min(max(keyword_growth, 0.0), 25.0)
                    - min(competition * 20.0, 30.0),
                ),
            )
            return self._signal(
                keyword=keyword,
                region=region,
                value=value,
                confidence=0.88,
                is_real=True,
                api_status="REAL",
                metrics=metrics,
            )
        except Exception as exc:
            return self._unavailable(keyword=keyword, region=region, error_detail=f"SEO provider 失败: {exc}")

    def _missing_credentials(self) -> list[str]:
        if str(settings.dataforseo_login or "").strip() and str(settings.dataforseo_password or "").strip():
            return []
        if str(settings.bing_webmaster_api_key or "").strip():
            return []
        return ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"]

    async def _fetch_dataforseo(self, *, keyword: str, region: str) -> dict:
        login = str(settings.dataforseo_login or "").strip()
        password = str(settings.dataforseo_password or "").strip()
        if not login or not password:
            raise ValueError("DATAFORSEO_NOT_CONFIGURED")
        location_code = {"US": 2840, "UK": 2826, "GB": 2826, "EU": 1000}.get(str(region or "US").upper(), 2840)
        base_url = str(settings.dataforseo_base_url or "https://api.dataforseo.com").strip().rstrip("/")
        payload = [{
            "keywords": [keyword],
            "location_code": location_code,
            "language_code": "en",
            "include_clickstream_data": True,
        }]
        async with httpx.AsyncClient(auth=(login, password), timeout=30) as client:
            search_resp = await client.post(f"{base_url}/v3/dataforseo_labs/google/keyword_ideas/live", json=payload)
            search_resp.raise_for_status()
            volume_resp = await client.post(f"{base_url}/v3/keywords_data/google_ads/search_volume/live", json=payload)
            volume_resp.raise_for_status()
        search_tasks = (((search_resp.json() or {}).get("tasks")) or [])
        volume_tasks = (((volume_resp.json() or {}).get("tasks")) or [])
        search_items = (((search_tasks[0] or {}).get("result")) or []) if search_tasks else []
        volume_items = (((volume_tasks[0] or {}).get("result")) or []) if volume_tasks else []
        related_keywords = []
        competition_values = []
        growth_values = []
        cpc_values = []
        for item in search_items[:20]:
            kw = str(item.get("keyword") or "").strip()
            if kw:
                related_keywords.append(kw)
            if item.get("competition") is not None:
                competition_values.append(float(item.get("competition") or 0))
            if item.get("keyword_info", {}).get("cpc") is not None:
                cpc_values.append(float(item.get("keyword_info", {}).get("cpc") or 0))
        search_volume = 0.0
        for item in volume_items[:10]:
            info = item.get("keyword_info") or {}
            if info.get("search_volume") is not None:
                search_volume = float(info.get("search_volume") or 0)
            if info.get("competition") is not None:
                competition_values.append(float(info.get("competition") or 0))
            monthly = list(info.get("monthly_searches") or [])
            if len(monthly) >= 2:
                growth_values.append(float(monthly[-1].get("search_volume") or 0) - float(monthly[0].get("search_volume") or 0))
            if info.get("cpc") is not None:
                cpc_values.append(float(info.get("cpc") or 0))
        return {
            "search_volume": round(search_volume, 2),
            "cpc": round(mean(cpc_values), 2) if cpc_values else 0.0,
            "competition": round(mean(competition_values), 4) if competition_values else 0.0,
            "keyword_growth": round(mean(growth_values), 2) if growth_values else 0.0,
            "related_keywords": related_keywords[:10],
            "source_type": "dataforseo",
        }
