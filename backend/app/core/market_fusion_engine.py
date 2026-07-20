from __future__ import annotations

import asyncio
from statistics import mean

from pydantic import BaseModel, Field

from app.adapters.market.v3 import MarketSignal
from app.adapters.market.v3.amazon_provider import AmazonMarketProviderV3
from app.adapters.market.v3.meta_provider import MetaMarketProvider
from app.adapters.market.v3.pinterest_provider import PinterestMarketProvider
from app.adapters.market.v3.seo_provider import SeoMarketProviderV3
from app.adapters.market.v3.shopify_provider import ShopifyMarketProviderV3
from app.adapters.market.v3.tiktok_provider import TikTokMarketProviderV3
from app.core.market_opportunity_score import market_opportunity_score
from app.core.market_risk_engine import market_risk_engine
from app.core.market_signal_model import MarketSignalModel


class MarketRealityScore(BaseModel):
    score: float
    confidence: float
    real_source_ratio: float
    data_sources: dict[str, dict] = Field(default_factory=dict)
    risk_flags: list[str] = Field(default_factory=list)
    missing_credentials: list[str] = Field(default_factory=list)


class MarketFusionEngine:
    def __init__(self) -> None:
        self.providers = {
            "amazon": AmazonMarketProviderV3(),
            "tiktok": TikTokMarketProviderV3(),
            "meta": MetaMarketProvider(),
            "seo": SeoMarketProviderV3(),
            "shopify": ShopifyMarketProviderV3(),
            "pinterest": PinterestMarketProvider(),
        }

    def analyze(self, *, keyword: str, region: str, category: str | None = None) -> dict:
        return asyncio.run(self.analyze_async(keyword=keyword, region=region, category=category))

    async def analyze_async(self, *, keyword: str, region: str, category: str | None = None) -> dict:
        results = await asyncio.gather(*[
            provider.fetch_signal(keyword=keyword, region=region, category=category)
            for provider in self.providers.values()
        ])
        signal_map: dict[str, MarketSignal] = {signal.source: signal for signal in results}
        production_signals = [item for item in results if item.is_real and item.api_status in {"REAL", "PUBLIC_REAL"}]
        seo_signal = signal_map["seo"]
        amazon_signal = signal_map["amazon"]
        tiktok_signal = signal_map["tiktok"]
        meta_signal = signal_map["meta"]
        shopify_signal = signal_map["shopify"]

        realness_values = [self._realness_value(item.api_status) for item in results]
        real_data_ratio = round(sum(realness_values) / max(len(realness_values), 1), 4)
        demand = self._avg([
            float(amazon_signal.metrics.get("amazon_demand_score", amazon_signal.value)),
            float(seo_signal.metrics.get("search_volume") or 0) / 100.0,
            float(shopify_signal.metrics.get("selling_signal", shopify_signal.value)),
        ])
        trend = self._avg([
            float(tiktok_signal.metrics.get("trend_score", tiktok_signal.metrics.get("tiktok_trend_score", tiktok_signal.value))),
            float(seo_signal.metrics.get("keyword_growth") or 0),
            float(shopify_signal.metrics.get("category_activity") or 0),
        ])
        purchase_signal = self._avg([
            float(shopify_signal.metrics.get("selling_signal", shopify_signal.value)),
            float(amazon_signal.metrics.get("price_range", {}).get("average") or 0),
        ])
        competition = self._avg([
            float(amazon_signal.metrics.get("competition_score") or amazon_signal.metrics.get("search_results", 0) / 100.0),
            float(meta_signal.metrics.get("competition_score") or meta_signal.metrics.get("ad_competition") or 0),
            float(seo_signal.metrics.get("competition") or 0) * 100.0,
        ])
        seasonality_risk = max(0.0, min(100.0, 100.0 - float(tiktok_signal.metrics.get("growth_rate", tiktok_signal.metrics.get("hashtag_growth") or 0))))
        historical_score = market_opportunity_score.historical_score([])
        market_score = market_opportunity_score.score(
            amazon_score=float(amazon_signal.value),
            tiktok_score=float(tiktok_signal.value),
            meta_score=float(meta_signal.value),
            seo_score=float(seo_signal.value),
            shopify_score=float(shopify_signal.value),
            historical_score=historical_score,
        )
        confidence = round(
            max(
                0.0,
                min(
                    1.0,
                    mean([item.confidence for item in production_signals]) if production_signals else 0.0,
                ),
            ),
            4,
        )
        if any(item.api_status in {"CONFIG_REQUIRED", "UNAVAILABLE"} for item in results):
            confidence = round(max(0.0, confidence - 0.1), 4)
        if any(not item.is_real for item in results):
            confidence = round(max(0.0, confidence - 0.05), 4)
        score = round(market_score, 2)
        risk_flags = market_risk_engine.evaluate(
            market_score=score,
            real_data_ratio=real_data_ratio,
            competition_score=competition,
            trend_score=trend,
            historical_score=historical_score,
        )
        if real_data_ratio < 0.9:
            risk_flags.append("real_source_ratio_below_target")
        missing_credentials = sorted({
            credential
            for item in results
            for credential in item.missing_credentials
        })
        signal_model = MarketSignalModel(
            keyword=keyword,
            region=region,
            amazon_signal=amazon_signal.metrics,
            tiktok_signal=tiktok_signal.metrics,
            meta_signal=meta_signal.metrics,
            seo_signal=seo_signal.metrics,
            shopify_signal=shopify_signal.metrics,
            data_quality_score=round(confidence * 100, 2),
            real_data_ratio=real_data_ratio,
        )
        reality = MarketRealityScore(
            score=score,
            confidence=confidence,
            real_source_ratio=real_data_ratio,
            data_sources={key: signal.model_dump(mode="json") for key, signal in signal_map.items()},
            risk_flags=sorted(set(risk_flags)),
            missing_credentials=missing_credentials,
        )
        return {
            "keyword": keyword,
            "region": region,
            "demand": round(min(demand, 100.0), 2),
            "trend": round(min(trend, 100.0), 2),
            "purchase_signal": round(purchase_signal, 2),
            "competition": round(min(competition, 100.0), 2),
            "seasonality_risk": round(seasonality_risk, 2),
            "market_signal_model": signal_model.model_dump(mode="json"),
            "market_reality": reality.model_dump(mode="json"),
        }

    def _avg(self, values: list[float], *, clamp: bool = True) -> float:
        normalized = [float(value or 0) for value in values if value is not None]
        if not normalized:
            return 0.0
        value = mean(normalized)
        return max(0.0, min(100.0, value)) if clamp else value

    def _realness_value(self, api_status: str) -> float:
        normalized = str(api_status or "").upper()
        if normalized == "REAL":
            return 1.0
        if normalized in {"AUTHORIZED_REAL", "USER_AUTH_REAL"}:
            return 1.0
        if normalized == "CACHED_REAL":
            return 0.7
        if normalized == "PUBLIC_REAL":
            return 0.5
        return 0.0


market_fusion_engine = MarketFusionEngine()
