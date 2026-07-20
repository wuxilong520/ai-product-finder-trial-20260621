from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from app.adapters.market.v3 import MarketDataProvider, MarketSignal
from app.core.config import settings


class TikTokMarketProviderV3(MarketDataProvider):
    provider_name = "tiktok"

    async def fetch_signal(
        self,
        *,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> MarketSignal:
        del category
        if str(settings.tiktok_marketing_access_token or "").strip():
            return await self._from_marketing_api(keyword=keyword, region=region)
        return await self._from_creative_center(keyword=keyword, region=region)

    async def _from_marketing_api(self, *, keyword: str, region: str) -> MarketSignal:
        advertiser_id = str(settings.tiktok_advertiser_id or "").strip()
        if not advertiser_id:
            return self._config_required(
                keyword=keyword,
                region=region,
                missing_credentials=["TIKTOK_ADVERTISER_ID"],
                error_detail="TikTok Marketing API 还缺 advertiser_id",
            )
        try:
            endpoint = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
            headers = {
                "Access-Token": str(settings.tiktok_marketing_access_token or "").strip(),
                "Content-Type": "application/json",
            }
            payload = {
                "advertiser_id": advertiser_id,
                "dimensions": ["campaign_id"],
                "metrics": ["impressions", "clicks", "spend"],
                "data_level": "AUCTION_AD",
                "page": 1,
                "page_size": 20,
                "filtering": {"keyword": keyword},
            }
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = (response.json() or {}).get("data") or {}
            rows = list(data.get("list") or [])
            video_count = float(len(rows))
            engagement_signal = float(sum(float(item.get("clicks") or 0) for item in rows))
            hashtag_growth = min(100.0, engagement_signal / 20.0 + video_count * 3)
            trend_score = max(0.0, min(100.0, hashtag_growth * 0.6 + min(video_count * 5, 40.0)))
            return self._signal(
                keyword=keyword,
                region=region,
                value=trend_score,
                confidence=0.82,
                is_real=True,
                api_status="REAL",
                metrics={
                    "hashtag_growth": round(hashtag_growth, 2),
                    "video_count": int(video_count),
                    "engagement_signal": round(engagement_signal, 2),
                    "growth_rate": round(hashtag_growth - 20, 2),
                    "product_heat": round(trend_score, 2),
                    "region": region,
                    "tiktok_trend_score": round(trend_score, 2),
                    "trend_score": round(trend_score, 2),
                },
            )
        except Exception as exc:
            return self._unavailable(keyword=keyword, region=region, error_detail=f"TikTok Marketing API 失败: {exc}")

    async def _from_creative_center(self, *, keyword: str, region: str) -> MarketSignal:
        url = f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en?keyword={quote_plus(keyword)}"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            if response.status_code != 200:
                return self._unavailable(
                    keyword=keyword,
                    region=region,
                    error_detail=f"TikTok Creative Center 返回 {response.status_code}",
                )
            html = response.text
            keyword_hits = html.lower().count(keyword.lower())
            if keyword_hits <= 0:
                return self._unavailable(
                    keyword=keyword,
                    region=region,
                    error_detail="TikTok Creative Center 页面没有匹配到关键词信号",
                )
            hashtag_growth = min(100.0, 20 + keyword_hits * 1.5)
            video_count = min(2000, keyword_hits * 8)
            engagement_signal = min(100.0, 15 + keyword_hits * 1.2)
            trend_score = min(100.0, hashtag_growth * 0.45 + engagement_signal * 0.35 + min(video_count / 40.0, 20.0))
            return self._signal(
                keyword=keyword,
                region=region,
                value=trend_score,
                confidence=0.55,
                is_real=True,
                api_status="PUBLIC_REAL",
                metrics={
                    "hashtag_growth": round(hashtag_growth, 2),
                    "video_count": int(video_count),
                    "engagement_signal": round(engagement_signal, 2),
                    "growth_rate": round(hashtag_growth - 20, 2),
                    "product_heat": round(trend_score, 2),
                    "region": region,
                    "tiktok_trend_score": round(trend_score, 2),
                    "trend_score": round(trend_score, 2),
                },
            )
        except Exception as exc:
            return self._unavailable(keyword=keyword, region=region, error_detail=f"TikTok Creative Center 失败: {exc}")
