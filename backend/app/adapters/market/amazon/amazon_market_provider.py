from __future__ import annotations

import re
from statistics import mean
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from app.adapters.market.base import MarketProvider


class AmazonMarketProvider(MarketProvider):
    provider_name = "amazon"
    search_url = "https://www.amazon.com/s"

    async def fetch_market_signal(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
        time_range: str = "90d",
    ) -> dict:
        del region, category, time_range
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
                return self._unavailable(reason=f"amazon_http_{response.status_code}")

            signal = self._parse_page(keyword=keyword, html=response.text)
            source_status = "verified" if signal["review_count"] > 0 and signal["price_range"]["max"] > 0 else "partial"
            confidence = 0.74 if source_status == "verified" else 0.48
            return self._signal_envelope(
                source=self.provider_name,
                source_status=source_status,
                signal=signal,
                confidence=confidence,
            )
        except Exception as exc:
            return self._unavailable(reason=f"amazon_exception:{exc}")

    def _parse_page(self, *, keyword: str, html: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        result_cards = soup.select("[data-component-type='s-search-result']")
        prices: list[float] = []
        ratings: list[float] = []
        review_counts: list[int] = []
        seller_count = 0
        keyword_positions: list[int] = []

        for index, card in enumerate(result_cards[:16], start=1):
            title = " ".join(card.stripped_strings).lower()
            if keyword.lower() in title:
                keyword_positions.append(index)
            price_node = card.select_one("span.a-price > span.a-offscreen")
            if price_node:
                raw_price = price_node.get_text(strip=True).replace("$", "").replace(",", "")
                try:
                    prices.append(float(raw_price))
                except ValueError:
                    pass
            rating_node = card.select_one("span.a-icon-alt")
            if rating_node:
                match = re.search(r"([0-9.]+)\s+out of", rating_node.get_text(" ", strip=True), re.IGNORECASE)
                if match:
                    ratings.append(float(match.group(1)))
            review_node = card.select_one("span.a-size-base.s-underline-text")
            if review_node:
                raw_review = review_node.get_text(strip=True).replace(",", "")
                if raw_review.isdigit():
                    review_counts.append(int(raw_review))
            if "sold by" in title or "ships from" in title:
                seller_count += 1

        body_text = soup.get_text(" ", strip=True)
        product_count = self._extract_result_count(body_text)
        average_price = round(mean(prices), 2) if prices else 0.0
        bsr_rank = max(1, keyword_positions[0] if keyword_positions else 999)
        review_count = int(round(mean(review_counts))) if review_counts else 0
        rating = round(mean(ratings), 2) if ratings else 0.0
        competition_density = round(
            min(100.0, (product_count / 120.0) + (seller_count * 3.2) + (len(result_cards) * 1.1)),
            2,
        )
        keyword_position = keyword_positions[0] if keyword_positions else 0
        demand_score = round(
            min(
                100.0,
                (35 if product_count else 0)
                + min(product_count / 150.0, 35.0)
                + min(review_count / 60.0, 20.0)
                + min(rating * 4.0, 10.0),
            ),
            2,
        )
        return {
            "keyword": keyword,
            "bsr_rank": bsr_rank,
            "review_count": review_count,
            "rating": rating,
            "seller_count": seller_count,
            "price_range": {
                "min": round(min(prices), 2) if prices else 0.0,
                "max": round(max(prices), 2) if prices else 0.0,
                "average": average_price,
            },
            "competition_density": competition_density,
            "keyword_position": keyword_position,
            "product_count": product_count,
            "demand_score": demand_score,
        }

    def _extract_result_count(self, body_text: str) -> int:
        match = re.search(r"([0-9,]+)\s+results", body_text, re.IGNORECASE)
        if not match:
            return 0
        try:
            return int(match.group(1).replace(",", ""))
        except ValueError:
            return 0

    def _unavailable(self, *, reason: str) -> dict:
        return self._signal_envelope(
            source=self.provider_name,
            source_status="unavailable",
            confidence=0.0,
            signal={
                "bsr_rank": 0,
                "review_count": 0,
                "rating": 0.0,
                "seller_count": 0,
                "price_range": {"min": 0.0, "max": 0.0, "average": 0.0},
                "competition_density": 0.0,
                "keyword_position": 0,
                "product_count": 0,
                "demand_score": 0.0,
                "reason": reason,
            },
        )
