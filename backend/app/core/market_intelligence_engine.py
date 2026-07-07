from __future__ import annotations

from statistics import mean

from pydantic import BaseModel, Field

from app.adapters.market.amazon_adapter import AmazonMarketAdapter
from app.adapters.market.google_trends_adapter import GoogleTrendsAdapter
from app.adapters.market.shopify_category_adapter import ShopifyCategoryAdapter
from app.adapters.market.tiktok_trends_adapter import TikTokTrendsAdapter


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
    demand_score: float
    trend_strength: float
    competition_level: str
    market_saturation: float
    entry_barrier: str
    platform_signals: PlatformSignals
    keyword_cluster: KeywordCluster
    platform_compatibility: PlatformCompatibility
    is_mock: bool
    mock_penalty: float
    confidence: float
    data_source_map: dict[str, str]


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
        self.tiktok = TikTokTrendsAdapter()
        self.shopify = ShopifyCategoryAdapter()

    def analyze(self, query: MarketQuery) -> MarketInsight:
        normalized_keyword = query.keyword.strip()
        google_payload = self._read_adapter(self.google, normalized_keyword, query.region)
        amazon_payload = self._read_adapter(self.amazon, normalized_keyword, "amazon")
        tiktok_payload = self._read_adapter(self.tiktok, normalized_keyword, "tiktok")
        shopify_payload = self._read_adapter(self.shopify, normalized_keyword, "shopify")

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
        market_saturation = round(min(100.0, competition_score * 0.9 + shopify_payload["competition_score"] * 0.1), 2)
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

        market_score = self.compute_market_score(
            MarketIntelligence(
                demand_score=round(demand_score, 2),
                trend_strength=round(trend_strength, 2),
                competition_level=competition_level,
                market_saturation=market_saturation,
                entry_barrier=entry_barrier,
                platform_signals=signals,
                keyword_cluster=self._build_keyword_cluster(normalized_keyword),
                platform_compatibility=PlatformCompatibility(
                    shopify_ready=False,
                    alibaba_match=self._build_alibaba_match(normalized_keyword),
                    tiktok_potential=round(signals.tiktok_viral_score, 2),
                ),
                is_mock=is_mock,
                mock_penalty=mock_penalty,
                confidence=confidence,
                data_source_map={
                    "google": google_payload["source"],
                    "amazon": amazon_payload["source"],
                    "tiktok": tiktok_payload["source"],
                    "shopify": shopify_payload["source"],
                },
            )
        )

        intelligence = MarketIntelligence(
            demand_score=round(demand_score, 2),
            trend_strength=round(trend_strength, 2),
            competition_level=competition_level,
            market_saturation=market_saturation,
            entry_barrier=entry_barrier,
            platform_signals=signals,
            keyword_cluster=self._build_keyword_cluster(normalized_keyword),
            platform_compatibility=PlatformCompatibility(
                shopify_ready=market_score >= 55,
                alibaba_match=self._build_alibaba_match(normalized_keyword),
                tiktok_potential=round(signals.tiktok_viral_score, 2),
            ),
            is_mock=is_mock,
            mock_penalty=mock_penalty,
            confidence=confidence,
            data_source_map={
                "google": google_payload["source"],
                "amazon": amazon_payload["source"],
                "tiktok": tiktok_payload["source"],
                "shopify": shopify_payload["source"],
            },
        )
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
                "demand_reason": f"需求基础分 {intelligence.demand_score}，核心由 Google / Amazon / TikTok 信号加权得出。",
                "competition_reason": f"市场饱和度 {intelligence.market_saturation}，当前竞争等级为 {intelligence.competition_level}。",
                "trend_reason": f"趋势强度 {intelligence.trend_strength}，当前推荐结论为 {recommendation}。",
            },
            risk_flags=risk_flags,
            market_intelligence=intelligence,
        )

    def compute_market_score(self, data: MarketIntelligence) -> float:
        demand = self._weighted_average(
            data.platform_signals.google_trends_score,
            data.platform_signals.amazon_search_volume,
            data.platform_signals.tiktok_viral_score,
        )
        competition_penalty = self._competition_penalty(
            competition_level=data.competition_level,
            saturation=data.market_saturation,
        )
        trend_boost = data.trend_strength * 0.2
        return self._clamp(demand - competition_penalty + trend_boost)

    def _read_adapter(self, adapter, keyword: str, market: str) -> dict:
        payload = adapter.fetch_market_insight(keyword=keyword, market=market)
        demand_score = float(payload.demand_score)
        competition_score = float(payload.competition_score)
        trend_strength = float(payload.trend_points[-1].score if payload.trend_points else payload.demand_score)
        is_mock = "mock" in str(payload.source).lower() or "placeholder" in str(payload.source).lower()
        return {
            "source": payload.source,
            "demand_score": demand_score,
            "competition_score": competition_score,
            "trend_strength": trend_strength,
            "is_mock": is_mock,
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
        if market_score >= 68:
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

    def _build_keyword_cluster(self, keyword: str) -> KeywordCluster:
        return KeywordCluster(
            related_keywords=[
                keyword,
                f"{keyword} for travel",
                f"{keyword} bluetooth",
            ],
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
            f"{keyword} factory",
        ]

    def _compute_confidence(self, *, google_payload: dict, amazon_payload: dict, tiktok_payload: dict, shopify_payload: dict) -> float:
        payloads = [google_payload, amazon_payload, tiktok_payload, shopify_payload]
        completeness = sum(1 for payload in payloads if payload["source"]) / len(payloads)
        return round(max(0.0, min(1.0, 0.55 + (completeness * 0.35))), 2)

    def _band(self, value: float, *, low_cut: float, high_cut: float) -> str:
        if value >= high_cut:
            return "high"
        if value >= low_cut:
            return "medium"
        return "low"

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, value)), 2)


market_intelligence_engine = MarketIntelligenceEngine()
