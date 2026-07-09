from __future__ import annotations

import re
from statistics import mean
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from app.adapters.market.market_base import MarketDataAdapter


class AmazonMarketAdapter(MarketDataAdapter):
    source_name = "amazon_market_public"
    search_url = "https://www.amazon.com/s"

    async def fetch(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> dict:
        del region, category
        try:
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(f"{self.search_url}?k={quote_plus(keyword)}")
            if response.status_code != 200:
                return self._fallback(
                    keyword=keyword,
                    reason=f"amazon_http_{response.status_code}",
                    source_status="public_blocked",
                )
            parsed = self._parse_page(keyword=keyword, html=response.text)
            source_status = "real" if parsed["average_price"] > 0 else "partial"
            return self._envelope(
                source=f"{self.source_name}_{source_status}",
                data=parsed,
                confidence=0.68 if source_status == "real" else 0.46,
                is_mock=False,
                source_status=source_status,
            )
        except Exception as exc:
            return self._fallback(
                keyword=keyword,
                reason=f"amazon_exception:{exc}",
                source_status="pending",
            )

    def _parse_page(self, *, keyword: str, html: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        body_text = soup.get_text(" ", strip=True)
        count_match = re.search(r"([0-9,]+)\s+results", body_text, re.IGNORECASE)
        product_count = int(count_match.group(1).replace(",", "")) if count_match else 0

        prices: list[float] = []
        for node in soup.select("span.a-price > span.a-offscreen")[:12]:
            raw = node.get_text(strip=True).replace("$", "").replace(",", "")
            try:
                prices.append(float(raw))
            except ValueError:
                continue

        average_price = round(mean(prices), 2) if prices else 0.0
        price_min = round(min(prices), 2) if prices else 0.0
        price_max = round(max(prices), 2) if prices else 0.0
        bestseller_count = len(re.findall(r"best seller", body_text, re.IGNORECASE))
        review_density = min(100.0, round((len(re.findall(r"rating", body_text, re.IGNORECASE)) / max(len(prices), 1)) * 12, 2))
        competition_level = "high" if product_count >= 5000 else "medium" if product_count >= 1000 else "low"
        market_signal = min(
            100.0,
            round(
                (35.0 if product_count else 0.0)
                + min(product_count / 120, 40.0)
                + (25.0 if prices else 0.0),
                2,
            ),
        )
        demand_indicator = round(min(100.0, market_signal + min(bestseller_count * 3, 12)), 2)
        competition_indicator = round(min(100.0, (80 if competition_level == "high" else 58 if competition_level == "medium" else 32) + min(product_count / 800, 15)), 2)
        category_strength = round(min(100.0, demand_indicator * 0.65 + review_density * 0.35), 2)
        return {
            "keyword": keyword,
            "competition_level": competition_level,
            "average_price": average_price,
            "product_count": product_count,
            "market_signal": market_signal,
            "demand_indicator": demand_indicator,
            "competition_indicator": competition_indicator,
            "price_range": {"min": price_min, "max": price_max},
            "category_strength": category_strength,
            "bestseller_count": bestseller_count,
            "review_density": review_density,
            "competition_product_count": product_count,
        }

    def _fallback(self, *, keyword: str, reason: str, source_status: str) -> dict:
        return self._envelope(
            source=f"{self.source_name}_mock",
            data={
                "keyword": keyword,
                "competition_level": "medium",
                "average_price": 39.9,
                "product_count": 0,
                "market_signal": 42.0,
                "demand_indicator": 42.0,
                "competition_indicator": 55.0,
                "price_range": {"min": 29.9, "max": 49.9},
                "category_strength": 38.0,
                "bestseller_count": 0,
                "review_density": 0.0,
                "competition_product_count": 0,
                "fallback_reason": reason,
            },
            confidence=0.22,
            is_mock=True,
            source_status=source_status,
        )
