from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from .global_market_base import GlobalMarketProvider, MarketSignal


class TikTokTrendProvider(GlobalMarketProvider):
    source_name = "tiktok"
    signal_type = "content_trend"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        url = f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en?keyword={quote_plus(keyword)}"
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
            if keyword_hits <= 0:
                raise ValueError("keyword not found")
            trend_score = min(100.0, 12 + keyword_hits * 1.8)
            growth = min(100.0, 8 + keyword_hits * 1.2)
            trend = "up" if growth >= 20 else "flat"
            return self.build_signal(
                keyword=keyword,
                country=country,
                value=trend_score,
                trend=trend,
                confidence=0.58,
                data_status="real",
                metrics={
                    "tiktok_trend_score": round(trend_score, 2),
                    "content_growth": round(growth, 2),
                    "country_signal": country.upper(),
                    "hashtag_hits": keyword_hits,
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
                error_detail=f"TikTok Creative Center failed: {exc}",
            )
