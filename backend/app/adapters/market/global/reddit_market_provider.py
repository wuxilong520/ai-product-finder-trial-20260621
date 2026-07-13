from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from .global_market_base import GlobalMarketProvider, MarketSignal


class RedditMarketProvider(GlobalMarketProvider):
    source_name = "reddit"
    signal_type = "consumer_discussion"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        del country
        url = f"https://www.reddit.com/search/?q={quote_plus(keyword)}&sort=relevance&t=month"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            html = response.text.lower()
            post_hits = html.count("/comments/")
            comment_hits = html.count(" comments")
            pain_points = [
                item for item in ["battery", "noise", "latency", "comfort", "price", "quality"]
                if item in html
            ]
            if post_hits <= 0 and comment_hits <= 0:
                raise ValueError("reddit search result empty")
            consumer_interest = min(100.0, post_hits * 3 + comment_hits * 1.2)
            trend = "up" if post_hits >= 8 else "flat"
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=consumer_interest,
                trend=trend,
                confidence=0.66,
                data_status="real",
                metrics={
                    "reddit_demand_score": round(consumer_interest, 2),
                    "consumer_interest": round(consumer_interest, 2),
                    "post_count": post_hits,
                    "comment_activity": comment_hits,
                    "pain_point_keywords": pain_points[:8],
                },
            )
        except Exception as exc:
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=0,
                trend="flat",
                confidence=0.2,
                data_status="fallback",
                error_detail=f"Reddit public search failed: {exc}",
            )
