from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote_plus

import httpx

from app.models.commercial_signal import CommercialSignal


class TikTokBusinessProvider:
    source_name = "tiktok_ads"

    async def fetch_signal(self, keyword: str, region: str) -> CommercialSignal:
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
            advertiser_hits = html.count("advertiser") + html.count("sponsored")
            if keyword_hits <= 0:
                raise ValueError("keyword not found in creative center")
            score = min(100.0, 18 + keyword_hits * 1.6 + advertiser_hits * 1.1)
            return CommercialSignal(
                source=self.source_name,
                signal_type="advertising",
                score=round(score, 2),
                reliability=0.58,
                timestamp=datetime.now(timezone.utc).isoformat(),
                is_real=True,
                status="limited",
                metadata={
                    "trend_keyword": keyword,
                    "video_growth": round(min(100.0, 10 + keyword_hits * 1.2), 2),
                    "advertiser_activity": advertiser_hits,
                    "country": str(region or "US").upper(),
                },
            )
        except Exception as exc:
            return CommercialSignal(
                source=self.source_name,
                signal_type="advertising",
                score=0.0,
                reliability=0.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                is_real=False,
                status="limited",
                metadata={"message": f"TikTok Creative Center 暂时不可稳定读取: {exc}"},
            )

