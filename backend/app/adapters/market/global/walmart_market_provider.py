from __future__ import annotations

import re
from statistics import mean
from urllib.parse import quote_plus

import httpx

from .global_market_base import GlobalMarketProvider, MarketSignal


class WalmartMarketProvider(GlobalMarketProvider):
    source_name = "walmart"
    signal_type = "retail_market"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        del country
        url = f"https://www.walmart.com/search?q={quote_plus(keyword)}"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            html = response.text
            item_hits = html.count('"usItemId"')
            visible_count = min(max(item_hits // 10, 12), 36)
            review_hits = [float(x) for x in re.findall(r'"numberOfReviews":\s*([0-9]+)', html)[:20]]
            prices = [float(x) for x in re.findall(r'"price":\s*([0-9]+(?:\.[0-9]+)?)', html)[:20]]
            if item_hits <= 0:
                raise ValueError("walmart search results empty")
            market_score = min(100.0, visible_count * 2.2 + min(sum(review_hits), 800) * 0.02)
            return self.build_signal(
                keyword=keyword,
                country="US",
                value=market_score,
                trend="up" if visible_count >= 12 else "flat",
                confidence=0.68,
                data_status="real",
                metrics={
                    "walmart_market_score": round(market_score, 2),
                    "product_count": visible_count,
                    "raw_item_hits": item_hits,
                    "review_scale": round(mean(review_hits), 2) if review_hits else 0.0,
                    "price_range": {
                        "min": round(min(prices), 2) if prices else 0.0,
                        "max": round(max(prices), 2) if prices else 0.0,
                        "average": round(mean(prices), 2) if prices else 0.0,
                    },
                },
            )
        except Exception as exc:
            return self.build_signal(
                keyword=keyword,
                country="US",
                value=0,
                trend="flat",
                confidence=0.2,
                data_status="fallback",
                error_detail=f"Walmart public search failed: {exc}",
            )
