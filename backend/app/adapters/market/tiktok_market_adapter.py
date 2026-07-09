from __future__ import annotations

import json
import re
from urllib.parse import quote

import httpx

from app.adapters.market.market_base import MarketDataAdapter


class TikTokMarketAdapter(MarketDataAdapter):
    source_name = "tiktok_market"

    async def fetch(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> dict:
        del region, category
        url = f"https://www.tiktok.com/tag/{quote(keyword.replace(' ', ''))}"
        try:
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            if response.status_code != 200:
                return self._pending(keyword=keyword, reason=f"tiktok_http_{response.status_code}")

            raw_data = self._extract_payload(response.text)
            if not raw_data:
                return self._pending(keyword=keyword, reason="tiktok_payload_missing")

            seo_abtest = raw_data.get("seo.abtest", {}) if isinstance(raw_data, dict) else {}
            vid_list = seo_abtest.get("vidList", []) if isinstance(seo_abtest, dict) else []
            keyword_frequency = response.text.lower().count(keyword.lower())
            video_count = len(vid_list)
            viral_score = min(100.0, round(18 + min(keyword_frequency, 120) * 0.35 + video_count * 6, 2))
            content_growth = min(100.0, round(10 + video_count * 4, 2))
            growth_rate = round(content_growth - 10, 2)
            return self._envelope(
                source=f"{self.source_name}_partial",
                data={
                    "viral_score": viral_score,
                    "content_growth": content_growth,
                    "growth_rate": growth_rate,
                    "keyword_frequency": keyword_frequency,
                    "video_count": video_count,
                    "confidence": 0.45,
                },
                confidence=0.45,
                is_mock=False,
                source_status="partial",
            )
        except Exception as exc:
            return self._pending(keyword=keyword, reason=f"tiktok_exception:{exc}")

    def _extract_payload(self, html: str) -> dict | None:
        match = re.search(
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
            html,
        )
        if not match:
            return None
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
        return payload.get("__DEFAULT_SCOPE__")

    def _pending(self, *, keyword: str, reason: str) -> dict:
        return self._envelope(
            source=f"{self.source_name}_pending",
            data={
                "viral_score": 38.0,
                "content_growth": 30.0,
                "growth_rate": 8.0,
                "keyword_frequency": 0,
                "video_count": 0,
                "confidence": 0.18,
                "keyword": keyword,
                "fallback_reason": reason,
            },
            confidence=0.18,
            is_mock=True,
            source_status="pending",
        )
