from __future__ import annotations

import re
from statistics import mean
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from .global_market_base import GlobalMarketProvider, MarketSignal


class AmazonPublicProvider(GlobalMarketProvider):
    source_name = "amazon"
    signal_type = "market_public"

    _PRICE_PATTERN = re.compile(r"([0-9]+(?:\.[0-9]+)?)")
    _REVIEW_PATTERN = re.compile(r"([0-9][0-9.,Kk+]*)")

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        domain = {"US": "www.amazon.com", "UK": "www.amazon.co.uk", "GB": "www.amazon.co.uk"}.get(str(country or "US").upper(), "www.amazon.com")
        url = f"https://{domain}/s?k={quote_plus(keyword)}"
        try:
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            html = response.text
            if "captcha" in html.lower():
                raise ValueError("amazon captcha")
            soup = BeautifulSoup(html, "lxml")
            cards = soup.select("[data-component-type='s-search-result']")
            prices = []
            reviews = []
            currency = ""
            for card in cards[:12]:
                price_node = self._pick_primary_price_node(card)
                if price_node:
                    price_text = price_node.get_text(" ", strip=True).replace(",", "")
                    currency = currency or self._detect_currency(price_text)
                    match = self._PRICE_PATTERN.search(price_text)
                    if match:
                        price_value = float(match.group(1))
                        if self._is_reasonable_price(price_value, currency):
                            prices.append(price_value)
                review_node = card.select_one(".s-underline-link-text.s-link-style, .a-link-normal.s-underline-text.s-underline-link-text")
                if review_node:
                    review_value = self._parse_review_count(review_node.get_text(" ", strip=True))
                    if review_value is not None:
                        reviews.append(review_value)
            market_score = min(100.0, len(cards) * 3 + min(mean(reviews), 60) * 0.3 if reviews else len(cards) * 2)
            trend = "up" if market_score >= 35 else "flat"
            return self.build_signal(
                keyword=keyword,
                country=country,
                value=market_score,
                trend=trend,
                confidence=0.7,
                data_status="real",
                metrics={
                    "amazon_market_score": round(market_score, 2),
                    "review_count": round(mean(reviews), 2) if reviews else 0.0,
                    "price_range": {
                        "min": round(min(prices), 2) if prices else 0.0,
                        "max": round(max(prices), 2) if prices else 0.0,
                        "average": round(mean(prices), 2) if prices else 0.0,
                        "currency": currency or "UNKNOWN",
                    },
                    "category_rank": len(cards),
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
                error_detail=f"Amazon public page failed: {exc}",
            )

    def _pick_primary_price_node(self, card) -> BeautifulSoup | None:
        current_price = card.select_one(".a-price[data-a-size='xl'] .a-offscreen, .a-price:not([data-a-strike='true']) .a-offscreen")
        if current_price:
            return current_price
        nodes = card.select(".a-price .a-offscreen")
        return nodes[0] if nodes else None

    def _parse_review_count(self, text: str) -> float | None:
        match = self._REVIEW_PATTERN.search(text.replace(",", ""))
        if not match:
            return None
        raw = match.group(1).rstrip("+")
        if raw.lower().endswith("k"):
            try:
                return float(raw[:-1]) * 1000
            except ValueError:
                return None
        try:
            value = float(raw)
        except ValueError:
            return None
        if value <= 5:
            return None
        return value

    def _detect_currency(self, text: str) -> str:
        normalized = text.upper()
        if "JPY" in normalized or "¥" in text:
            return "JPY"
        if "USD" in normalized or "$" in text:
            return "USD"
        if "GBP" in normalized or "£" in text:
            return "GBP"
        if "EUR" in normalized or "€" in text:
            return "EUR"
        return "UNKNOWN"

    def _is_reasonable_price(self, value: float, currency: str) -> bool:
        upper_limits = {
            "JPY": 200000,
            "USD": 1000,
            "GBP": 1000,
            "EUR": 1000,
            "UNKNOWN": 1000,
        }
        return 0 < value < upper_limits.get(currency or "UNKNOWN", 1000)
