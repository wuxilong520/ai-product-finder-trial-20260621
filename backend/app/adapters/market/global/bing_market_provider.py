from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from .global_market_base import GlobalMarketProvider, MarketSignal


class BingMarketProvider(GlobalMarketProvider):
    source_name = "bing"
    signal_type = "search_support"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        mkt = "en-US" if str(country or "US").upper() == "US" else "en-GB"
        url = f"https://www.bing.com/search?q={quote_plus(keyword)}&setlang=en-US&mkt={mkt}"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            html = response.text.lower()
            result_hits = max(
                html.count('class="b_algo"'),
                html.count("class='b_algo'"),
            )
            related_hits = html.count("related searches") + html.count("people also ask") + html.count("explore more")
            query_hits = html.count(keyword.lower())
            if result_hits <= 0:
                raise ValueError("bing results empty")
            search_signal = min(100.0, result_hits * 6 + related_hits * 8 + min(query_hits, 24) * 0.6)
            return self.build_signal(
                keyword=keyword,
                country=country,
                value=search_signal,
                trend="up" if related_hits >= 1 else "flat",
                confidence=0.72,
                data_status="real",
                metrics={
                    "bing_search_signal": round(search_signal, 2),
                    "result_count_proxy": result_hits,
                    "related_query_count": related_hits,
                    "query_presence": query_hits,
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
                error_detail=f"Bing public search failed: {exc}",
            )
