from __future__ import annotations

import json
import re
from urllib.parse import quote

import httpx

from app.adapters.market.base import MarketProvider


class TikTokMarketProvider(MarketProvider):
    provider_name = "tiktok"

    async def fetch_market_signal(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
        time_range: str = "90d",
    ) -> dict:
        del region, category, time_range
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
                return self._unavailable(reason=f"tiktok_http_{response.status_code}")
            raw_payload = self._extract_payload(response.text)
            if not raw_payload:
                return self._unavailable(reason="tiktok_payload_missing")

            seo_abtest = raw_payload.get("seo.abtest", {}) if isinstance(raw_payload, dict) else {}
            vid_list = seo_abtest.get("vidList", []) if isinstance(seo_abtest, dict) else []
            video_count = len(vid_list)
            keyword_frequency = response.text.lower().count(keyword.lower())
            creator_density = round(min(100.0, video_count * 7.5), 2)
            content_growth = round(min(100.0, 12 + video_count * 5.5), 2)
            viral_velocity = round(min(100.0, 20 + keyword_frequency * 0.8 + video_count * 4.0), 2)
            engagement_rate = round(min(100.0, 8 + video_count * 3.1), 2)
            trend_score = round(min(100.0, (viral_velocity * 0.4) + (content_growth * 0.35) + (engagement_rate * 0.25)), 2)
            return self._signal_envelope(
                source=self.provider_name,
                source_status="partial",
                confidence=0.42,
                signal={
                    "viral_velocity": viral_velocity,
                    "content_growth": content_growth,
                    "creator_density": creator_density,
                    "engagement_rate": engagement_rate,
                    "trend_score": trend_score,
                    "video_count": video_count,
                    "keyword_frequency": keyword_frequency,
                },
            )
        except Exception as exc:
            return self._unavailable(reason=f"tiktok_exception:{exc}")

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

    def _unavailable(self, *, reason: str) -> dict:
        return self._signal_envelope(
            source=self.provider_name,
            source_status="unavailable",
            confidence=0.0,
            signal={
                "viral_velocity": 0.0,
                "content_growth": 0.0,
                "creator_density": 0.0,
                "engagement_rate": 0.0,
                "trend_score": 0.0,
                "reason": reason,
            },
        )
