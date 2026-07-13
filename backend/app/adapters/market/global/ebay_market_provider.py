from __future__ import annotations

import re
from statistics import mean
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from .global_market_base import GlobalMarketProvider, MarketSignal


class EbayMarketProvider(GlobalMarketProvider):
    source_name = "ebay"
    signal_type = "public_marketplace"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        del country
        url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(keyword)}"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            cards = soup.select(".s-item")
            prices = []
            for card in cards[:20]:
                price_node = card.select_one(".s-item__price")
                if not price_node:
                    continue
                match = re.search(r"([0-9]+(?:\.[0-9]+)?)", price_node.get_text(" ", strip=True).replace(",", ""))
                if match:
                    prices.append(float(match.group(1)))
            if not cards:
                raise ValueError("ebay results empty")
            activity = min(100.0, len(cards) * 4)
            competition_score = min(100.0, len(cards) * 3.5)
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=activity,
                trend="up" if len(cards) >= 12 else "flat",
                confidence=0.61,
                data_status="real",
                metrics={
                    "ebay_competition_score": round(competition_score, 2),
                    "market_activity": round(activity, 2),
                    "listing_count": len(cards),
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
                country="global",
                value=0,
                trend="flat",
                confidence=0.2,
                data_status="fallback",
                error_detail=f"eBay public search failed: {exc}",
            )
