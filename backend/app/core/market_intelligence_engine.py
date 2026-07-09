from __future__ import annotations

import asyncio
from statistics import mean

from pydantic import BaseModel, Field

from app.adapters.market.amazon_market_adapter import AmazonMarketAdapter
from app.adapters.market.google_trends_adapter import GoogleTrendsAdapter
from app.adapters.market.shopify_market_adapter import ShopifyMarketAdapter
from app.adapters.market.tiktok_market_adapter import TikTokMarketAdapter


class MarketQuery(BaseModel):
    keyword: str
    region: str = "global"
    category: str | None = None
    platforms: list[str] = Field(default_factory=lambda: ["google", "amazon", "tiktok", "shopify"])


class PlatformSignals(BaseModel):
    google_trends_score: float
    amazon_search_volume: float
    tiktok_viral_score: float
    shopify_category_activity: float


class KeywordCluster(BaseModel):
    related_keywords: list[str]
    long_tail_keywords: list[str]


class PlatformCompatibility(BaseModel):
    shopify_ready: bool
    alibaba_match: list[str]
    tiktok_potential: float


class MarketIntelligence(BaseModel):
    keyword: str
    demand_score: float
    trend_strength: float
    competition_level: str
    market_saturation: float
    entry_barrier: str
    platform_signals: PlatformSignals
    keyword_cluster: KeywordCluster
    platform_compatibility: PlatformCompatibility
    data_sources: dict[str, dict]
    is_mock: bool
    mock_penalty: float
    confidence: float
    data_source_map: dict[str, str]
    source_status: dict[str, str] = Field(default_factory=dict)
    market_signals: list[dict] = Field(default_factory=list)
    market_growth: float = 0
    trend_direction: str = "flat"
    market_opportunity: dict = Field(default_factory=dict)
    all_sources_mock: bool = False
    trend_points: list[dict] = Field(default_factory=list)


class MarketInsight(BaseModel):
    market_score: float
    recommendation: str
    confidence: float
    reasoning: dict
    risk_flags: list[str]
    market_intelligence: MarketIntelligence


class MarketIntelligenceEngine:
    def __init__(self) -> None:
        self.google = GoogleTrendsAdapter()
        self.amazon = AmazonMarketAdapter()
        self.tiktok = TikTokMarketAdapter()
        self.shopify = ShopifyMarketAdapter()

    def analyze(self, query: MarketQuery) -> MarketInsight:
        return asyncio.run(self.analyze_async(query))

    async def analyze_async(self, query: MarketQuery) -> MarketInsight:
        normalized_keyword = query.keyword.strip()
        google_raw, amazon_raw, tiktok_raw, shopify_raw = await asyncio.gather(
            self.google.fetch(normalized_keyword, query.region, query.category),
            self.amazon.fetch(normalized_keyword, query.region, query.category),
            self.tiktok.fetch(normalized_keyword, query.region, query.category),
            self.shopify.fetch(normalized_keyword, query.region, query.category),
        )

        google_payload = self._read_google(google_raw)
        amazon_payload = self._read_amazon(amazon_raw)
        tiktok_payload = self._read_tiktok(tiktok_raw)
        shopify_payload = self._read_shopify(shopify_raw)

        signals = PlatformSignals(
            google_trends_score=google_payload["demand_score"],
            amazon_search_volume=amazon_payload["demand_score"],
            tiktok_viral_score=tiktok_payload["demand_score"],
            shopify_category_activity=shopify_payload["demand_score"],
        )
        competition_score = mean([
            google_payload["competition_score"],
            amazon_payload["competition_score"],
            tiktok_payload["competition_score"],
            shopify_payload["competition_score"],
        ])
        trend_strength = mean([
            google_payload["trend_strength"],
            amazon_payload["trend_strength"],
            tiktok_payload["trend_strength"],
            shopify_payload["trend_strength"],
        ])
        demand_score = self._weighted_average(
            google_payload["demand_score"],
            amazon_payload["demand_score"],
            tiktok_payload["demand_score"],
        )
        market_saturation = round(min(100.0, competition_score * 0.82 + shopify_payload["competition_score"] * 0.18), 2)
        competition_level = self._band(market_saturation, low_cut=35, high_cut=70)
        entry_barrier = self._band((competition_score + market_saturation) / 2, low_cut=40, high_cut=72)

        is_mock = any(payload["is_mock"] for payload in [google_payload, amazon_payload, tiktok_payload, shopify_payload])
        mock_penalty = 0.2 if is_mock else 0.0
        base_confidence = self._compute_confidence(
            google_payload=google_payload,
            amazon_payload=amazon_payload,
            tiktok_payload=tiktok_payload,
            shopify_payload=shopify_payload,
        )
        if is_mock:
            demand_score = round(demand_score * 0.8, 2)
            confidence = round(max(0.0, base_confidence - 0.3), 2)
        else:
            confidence = base_confidence

        intelligence = MarketIntelligence(
            keyword=normalized_keyword,
            demand_score=round(demand_score, 2),
            trend_strength=round(trend_strength, 2),
            competition_level=competition_level,
            market_saturation=market_saturation,
            entry_barrier=entry_barrier,
            platform_signals=signals,
            keyword_cluster=self._build_keyword_cluster(normalized_keyword, google_raw),
            platform_compatibility=PlatformCompatibility(
                shopify_ready=False,
                alibaba_match=self._build_alibaba_match(normalized_keyword),
                tiktok_potential=round(signals.tiktok_viral_score, 2),
            ),
            data_sources={
                "google": google_raw,
                "amazon": amazon_raw,
                "tiktok": tiktok_raw,
                "shopify": shopify_raw,
            },
            is_mock=is_mock,
            mock_penalty=mock_penalty,
            confidence=confidence,
            data_source_map={
                "google": str(google_raw.get("source") or ""),
                "amazon": str(amazon_raw.get("source") or ""),
                "tiktok": str(tiktok_raw.get("source") or ""),
                "shopify": str(shopify_raw.get("source") or ""),
            },
            trend_points=google_payload["trend_points"],
        )

        market_score = self.compute_market_score(intelligence)
        intelligence = intelligence.model_copy(update={
            "platform_compatibility": PlatformCompatibility(
                shopify_ready=market_score >= 55,
                alibaba_match=self._build_alibaba_match(normalized_keyword),
                tiktok_potential=round(signals.tiktok_viral_score, 2),
            )
        })

        recommendation = self._recommend(market_score)
        risk_flags = self._build_risk_flags(
            demand_score=intelligence.demand_score,
            competition_level=intelligence.competition_level,
            trend_strength=intelligence.trend_strength,
            is_mock=intelligence.is_mock,
        )
        return MarketInsight(
            market_score=round(market_score, 2),
            recommendation=recommendation,
            confidence=confidence,
            reasoning={
                "demand_reason": f"需求基础分 {intelligence.demand_score}，当前由 Google / Amazon / TikTok / Shopify 市场信号统一计算。",
                "competition_reason": f"市场饱和度 {intelligence.market_saturation}，竞争等级为 {intelligence.competition_level}。",
                "trend_reason": f"趋势强度 {intelligence.trend_strength}，最终市场评分 {round(market_score, 2)}，推荐结论为 {recommendation}。",
            },
            risk_flags=risk_flags,
            market_intelligence=intelligence,
        )

    def compute_market_score(self, data: MarketIntelligence) -> float:
        demand = float(data.demand_score)
        competition_penalty = self._competition_penalty(
            competition_level=data.competition_level,
            saturation=data.market_saturation,
        )
        trend_boost = data.trend_strength * 0.18
        platform_signal_boost = mean(
            [
                data.platform_signals.google_trends_score,
                data.platform_signals.amazon_search_volume,
                data.platform_signals.tiktok_viral_score,
                data.platform_signals.shopify_category_activity,
            ]
        ) * 0.12
        score = demand + trend_boost + platform_signal_boost - competition_penalty - (data.market_saturation * 0.1)
        if data.is_mock:
            score *= 0.82
        return self._clamp(score)

    def _read_google(self, payload: dict) -> dict:
        data = payload.get("data", {})
        return {
            "source": payload.get("source"),
            "demand_score": float(data.get("trend_value") or data.get("trend_score") or 0),
            "competition_score": max(12.0, 55.0 - (float(data.get("growth_rate") or 0) * 0.8)),
            "trend_strength": float(data.get("trend_value") or data.get("trend_score") or 0),
            "trend_points": data.get("trend_points") or [],
            "is_mock": bool(payload.get("is_mock")),
        }

    def _read_amazon(self, payload: dict) -> dict:
        data = payload.get("data", {})
        product_count = float(data.get("product_count") or 0)
        competition_level = str(data.get("competition_level") or "medium")
        competition_score = {"low": 35.0, "medium": 62.0, "high": 82.0}.get(competition_level, 62.0)
        return {
            "source": payload.get("source"),
            "demand_score": float(data.get("demand_indicator") or data.get("market_signal") or 0),
            "competition_score": min(100.0, float(data.get("competition_indicator") or competition_score + min(product_count / 1000, 12))),
            "trend_strength": float(data.get("category_strength") or data.get("market_signal") or 0),
            "trend_points": [],
            "is_mock": bool(payload.get("is_mock")),
        }

    def _read_tiktok(self, payload: dict) -> dict:
        data = payload.get("data", {})
        return {
            "source": payload.get("source"),
            "demand_score": float(data.get("viral_score") or 0),
            "competition_score": max(18.0, 68.0 - (float(data.get("growth_rate", data.get("content_growth")) or 0) * 0.4)),
            "trend_strength": float(data.get("growth_rate", data.get("content_growth")) or 0),
            "trend_points": [],
            "is_mock": bool(payload.get("is_mock")),
        }

    def _read_shopify(self, payload: dict) -> dict:
        data = payload.get("data", {})
        price_range = data.get("price_range") or {}
        demand_score = float(data.get("category_activity") or 0)
        price_span_penalty = min(abs(float(price_range.get("max") or 0) - float(price_range.get("min") or 0)) / 10, 10)
        return {
            "source": payload.get("source"),
            "demand_score": demand_score,
            "competition_score": min(100.0, max(22.0, float(data.get("store_count_signal") or 0) * 9 + price_span_penalty)),
            "trend_strength": float(data.get("growth_signal") or demand_score),
            "trend_points": [],
            "is_mock": bool(payload.get("is_mock")),
        }

    def _weighted_average(self, google_trends: float, amazon_search: float, tiktok_signal: float) -> float:
        return round((google_trends * 0.4) + (amazon_search * 0.35) + (tiktok_signal * 0.25), 2)

    def _competition_penalty(self, *, competition_level: str, saturation: float) -> float:
        level_penalty = {
            "low": 8.0,
            "medium": 18.0,
            "high": 30.0,
        }[competition_level]
        return round(level_penalty + (saturation * 0.18), 2)

    def _recommend(self, market_score: float) -> str:
        if market_score >= 70:
            return "BUY"
        if 40 <= market_score < 70:
            return "TEST"
        return "IGNORE"

    def _build_risk_flags(self, *, demand_score: float, competition_level: str, trend_strength: float, is_mock: bool) -> list[str]:
        flags: list[str] = []
        if demand_score < 45:
            flags.append("low_demand")
        if competition_level == "high":
            flags.append("high_competition")
        if trend_strength < 50:
            flags.append("unstable_trend")
        if is_mock:
            flags.append("mock_data_used")
        return flags

    def _build_keyword_cluster(self, keyword: str, google_payload: dict) -> KeywordCluster:
        google_keywords = google_payload.get("data", {}).get("related_keywords") or []
        related_keywords = [item for item in google_keywords if item][:6] or [
            keyword,
            f"{keyword} review",
            f"{keyword} supplier",
        ]
        return KeywordCluster(
            related_keywords=related_keywords,
            long_tail_keywords=[
                f"best {keyword} for dropshipping",
                f"low competition {keyword}",
                f"{keyword} supplier bundle",
            ],
        )

    def _build_alibaba_match(self, keyword: str) -> list[str]:
        return [
            keyword,
            f"{keyword} wholesale",
            f"{keyword} supplier",
        ]

    def _band(self, score: float, *, low_cut: float, high_cut: float) -> str:
        if score < low_cut:
            return "low"
        if score < high_cut:
            return "medium"
        return "high"

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, value)), 2)

    def _compute_confidence(self, *, google_payload: dict, amazon_payload: dict, tiktok_payload: dict, shopify_payload: dict) -> float:
        confidence = mean([
            0.85 if not google_payload["is_mock"] else 0.26,
            0.65 if not amazon_payload["is_mock"] else 0.22,
            0.5 if not tiktok_payload["is_mock"] else 0.18,
            0.78 if not shopify_payload["is_mock"] else 0.2,
        ])
        return round(confidence, 2)


market_intelligence_engine = MarketIntelligenceEngine()
