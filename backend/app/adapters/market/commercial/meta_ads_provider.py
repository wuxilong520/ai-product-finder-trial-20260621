from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote_plus

import httpx

from app.models.commercial_signal import CommercialSignal


class MetaCommercialAdsProvider:
    source_name = "meta_ads"

    async def fetch_signal(self, keyword: str, region: str) -> CommercialSignal:
        url = (
            "https://www.facebook.com/ads/library/"
            f"?active_status=active&ad_type=all&country={str(region or 'US').upper()}&is_targeted_country=false"
            f"&media_type=all&search_type=keyword_unordered&q={quote_plus(keyword)}"
        )
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            if response.status_code == 403:
                return CommercialSignal(
                    source=self.source_name,
                    signal_type="brand",
                    score=0.0,
                    reliability=0.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    is_real=False,
                    status="limited",
                    metadata={"message": "Meta Ads Library 返回 403，当前只能判定为受限。"},
                )
            response.raise_for_status()
            html = response.text.lower()
            active_ads_count = html.count(keyword.lower())
            brand_count = html.count("page name") + html.count("advertiser")
            category_activity = html.count("ad archive") + html.count("sponsored")
            score = min(100.0, active_ads_count * 1.4 + brand_count * 0.9 + category_activity * 0.4)
            return CommercialSignal(
                source=self.source_name,
                signal_type="brand",
                score=round(score, 2),
                reliability=0.46,
                timestamp=datetime.now(timezone.utc).isoformat(),
                is_real=True,
                status="limited",
                metadata={
                    "active_ads_count": active_ads_count,
                    "brand_count": brand_count,
                    "category_activity": category_activity,
                    "country": str(region or "US").upper(),
                },
            )
        except Exception as exc:
            return CommercialSignal(
                source=self.source_name,
                signal_type="brand",
                score=0.0,
                reliability=0.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                is_real=False,
                status="limited",
                metadata={"message": f"Meta Ads Library 读取失败: {exc}"},
            )

