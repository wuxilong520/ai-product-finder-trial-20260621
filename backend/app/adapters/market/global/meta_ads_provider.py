from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from .global_market_base import GlobalMarketProvider, MarketSignal


class MetaAdsProvider(GlobalMarketProvider):
    source_name = "meta"
    signal_type = "ads_market"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        url = (
            "https://www.facebook.com/ads/library/"
            f"?active_status=active&ad_type=all&country={str(country or 'US').upper()}&is_targeted_country=false"
            f"&media_type=all&search_type=keyword_unordered&q={quote_plus(keyword)}"
        )
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            html = response.text.lower()
            keyword_hits = html.count(keyword.lower())
            advertiser_hits = html.count("advertiser") + html.count("page name")
            ads_score = min(100.0, keyword_hits * 1.5 + advertiser_hits * 0.8)
            trend = "up" if ads_score >= 25 else "flat"
            return self.build_signal(
                keyword=keyword,
                country=country,
                value=ads_score,
                trend=trend,
                confidence=0.45,
                data_status="real",
                metrics={
                    "meta_ads_score": round(ads_score, 2),
                    "active_ads_count": keyword_hits,
                    "advertiser_count": advertiser_hits,
                    "country": country.upper(),
                },
            )
        except Exception as exc:
            return self.build_signal(
                keyword=keyword,
                country=country,
                value=0,
                trend="flat",
                confidence=0.2,
                data_status="fallback",
                error_detail=f"Meta Ads Library failed: {exc}",
            )
