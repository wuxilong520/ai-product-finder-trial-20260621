from __future__ import annotations

import asyncio
from statistics import mean

from pydantic import BaseModel, Field

from app.adapters.market.commercial.google_ads_provider import GoogleAdsProvider
from app.adapters.market.commercial.meta_ads_provider import MetaCommercialAdsProvider
from app.adapters.market.commercial.tiktok_business_provider import TikTokBusinessProvider
from app.models.commercial_signal import CommercialSignal


class CommercialSignalReport(BaseModel):
    commercial_score: float = 0.0
    commercial_competition: float = 0.0
    ad_market_value: float = 0.0
    brand_activity: float = 0.0
    purchase_readiness: float = 0.0
    confidence: float = 0.0
    sources: dict[str, dict] = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)


class CommercialSignalEngine:
    def __init__(self) -> None:
        self.google_ads = GoogleAdsProvider()
        self.tiktok_ads = TikTokBusinessProvider()
        self.meta_ads = MetaCommercialAdsProvider()

    async def analyze(
        self,
        *,
        keyword: str,
        region: str,
        market_signals: dict[str, dict],
    ) -> CommercialSignalReport:
        google_signal, tiktok_signal, meta_signal = await asyncio.gather(
            self.google_ads.fetch_signal(keyword, region),
            self.tiktok_ads.fetch_signal(keyword, region),
            self.meta_ads.fetch_signal(keyword, region),
        )
        amazon_payload = market_signals.get("amazon") or {}
        amazon_brand_count = self._amazon_brand_count(amazon_payload)
        amazon_commercial_score = min(
            100.0,
            float(amazon_payload.get("value") or 0) * 0.45
            + min(float(((amazon_payload.get("metrics") or {}).get("review_count") or 0)) / 50, 30)
            + min(amazon_brand_count * 2.5, 25),
        )
        amazon_signal = CommercialSignal(
            source="amazon_ads",
            signal_type="product",
            score=round(amazon_commercial_score, 2),
            reliability=max(0.0, min(1.0, float(amazon_payload.get("confidence") or 0))),
            timestamp=str(amazon_payload.get("timestamp") or ""),
            is_real=str(amazon_payload.get("data_status") or "") == "real",
            status=str(amazon_payload.get("data_status") or "fallback"),
            metadata={
                "best_seller_rank": float(((amazon_payload.get("metrics") or {}).get("category_rank") or 0)),
                "review_count": float(((amazon_payload.get("metrics") or {}).get("review_count") or 0)),
                "brand_count": amazon_brand_count,
                "price_range": (amazon_payload.get("metrics") or {}).get("price_range") or {},
            },
        )

        signals = [google_signal, tiktok_signal, meta_signal, amazon_signal]
        advertising_values = [item.score for item in [google_signal, tiktok_signal, meta_signal] if item.status in {"real", "limited"} and item.score > 0]
        brand_values = [item.score for item in [meta_signal, amazon_signal] if item.status in {"real", "limited"} and item.score > 0]
        competition_values = [item.score for item in signals if item.status in {"real", "limited"} and item.score > 0]
        ad_market_value = round(mean(advertising_values), 2) if advertising_values else 0.0
        brand_activity = round(mean(brand_values), 2) if brand_values else 0.0
        commercial_competition = round(mean(competition_values), 2) if competition_values else 0.0

        usable = [item for item in signals if item.status in {"real", "limited"}]
        confidence = round(mean([item.reliability for item in usable]), 4) if usable else 0.0
        commercial_score = round(
            max(
                0.0,
                min(
                    100.0,
                    ad_market_value * 0.4
                    + brand_activity * 0.3
                    + float(amazon_signal.score) * 0.3,
                ),
            ),
            2,
        )
        risks: list[str] = []
        if not usable:
            risks.append("no_usable_commercial_sources")
        if google_signal.status == "not_configured":
            risks.append("google_ads_not_configured")
        if meta_signal.status == "limited":
            risks.append("meta_ads_limited")
        if tiktok_signal.status == "limited" and tiktok_signal.score <= 0:
            risks.append("tiktok_ads_limited")

        return CommercialSignalReport(
            commercial_score=commercial_score,
            commercial_competition=commercial_competition,
            ad_market_value=ad_market_value,
            brand_activity=brand_activity,
            purchase_readiness=round(float(amazon_signal.score), 2),
            confidence=confidence,
            sources={
                item.source: {
                    "score": round(item.score, 2),
                    "reliability": round(item.reliability, 4),
                    "status": item.status,
                    "is_real": item.is_real,
                    "metadata": item.metadata,
                }
                for item in signals
            },
            risks=sorted(set(risks)),
        )

    def _amazon_brand_count(self, amazon_payload: dict) -> int:
        review_count = float(((amazon_payload.get("metrics") or {}).get("review_count") or 0))
        category_rank = float(((amazon_payload.get("metrics") or {}).get("category_rank") or 0))
        return int(max(1, min(20, round(category_rank / 2 + min(review_count / 500, 8)))))


commercial_signal_engine = CommercialSignalEngine()
