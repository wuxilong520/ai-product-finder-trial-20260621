from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from importlib import import_module
from statistics import mean

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter
from app.core.commercial_signal_engine import commercial_signal_engine
from app.core.commercial_intent_engine import commercial_intent_engine
from app.core.competition_pressure_engine import competition_pressure_engine
from app.core.consumer_interest_engine import consumer_interest_engine
from app.core.keyword_intelligence_engine import keyword_intelligence_engine
from app.core.market_confidence_engine import market_confidence_engine
from app.core.purchase_signal_engine import purchase_signal_engine
from app.core.trend_lifecycle_engine import trend_lifecycle_engine
from app.models.market_reality_signal import MarketRealitySignal
from app.repositories.commercial_signal_history import commercial_signal_history_repository
from app.repositories.market_reality_history import market_reality_history_repository
from app.repositories.market_signal_history import market_signal_history_repository

AmazonPublicProvider = import_module("app.adapters.market.global.amazon_public_provider").AmazonPublicProvider
BingSearchRealityProvider = import_module("app.adapters.market.reality.bing_search_provider").BingSearchRealityProvider
EbayMarketProvider = import_module("app.adapters.market.global.ebay_market_provider").EbayMarketProvider
GoogleTrendsProvider = import_module("app.adapters.market.global.google_trends_provider").GoogleTrendsProvider
MetaAdsProvider = import_module("app.adapters.market.global.meta_ads_provider").MetaAdsProvider
PinterestRealityProvider = import_module("app.adapters.market.reality.pinterest_provider").PinterestRealityProvider
RedditOfficialProvider = import_module("app.adapters.market.reality.reddit_official_provider").RedditOfficialProvider
TikTokTrendProvider = import_module("app.adapters.market.global.tiktok_trend_provider").TikTokTrendProvider
WalmartMarketProvider = import_module("app.adapters.market.global.walmart_market_provider").WalmartMarketProvider
YouTubeRealityProvider = import_module("app.adapters.market.reality.youtube_provider").YouTubeRealityProvider
MarketSignal = import_module("app.adapters.market.global.global_market_base").MarketSignal


class MarketRealityReport(BaseModel):
    market_score: float
    demand_score: float
    trend_score: float
    competition_score: float
    profit_potential: float
    real_data_ratio: float
    confidence_score: float
    evidence_sources: list[dict] = Field(default_factory=list)
    source_reliability: dict[str, float] = Field(default_factory=dict)
    risk_flags: list[str] = Field(default_factory=list)
    recommendation: str = "WATCH"
    source_status: dict[str, str] = Field(default_factory=dict)
    signals: dict[str, dict] = Field(default_factory=dict)
    consumer_interest: float = 0.0
    commercial_intent: float = 0.0
    competition_pressure: float = 0.0
    trend_stage: str = "stable"
    trend_lifecycle: str = "stable"
    commercial_signal: float = 0.0
    commercial_score: float = 0.0
    commercial_competition: float = 0.0
    ad_market_value: float = 0.0
    brand_activity: float = 0.0
    purchase_signal: float = 0.0
    commercial_source_status: dict[str, str] = Field(default_factory=dict)
    commercial_sources: dict[str, dict] = Field(default_factory=dict)
    reality_sources: list[dict] = Field(default_factory=list)
    opportunity_reason: str = ""


class MarketIntelligenceEngine:
    def __init__(self) -> None:
        self.google = GoogleTrendsProvider()
        self.tiktok = TikTokTrendProvider()
        self.meta = MetaAdsProvider()
        self.amazon = AmazonPublicProvider()
        self.reddit = RedditOfficialProvider()
        self.youtube = YouTubeRealityProvider()
        self.bing = BingSearchRealityProvider()
        self.ebay = EbayMarketProvider()
        self.walmart = WalmartMarketProvider()
        self.pinterest = PinterestRealityProvider()
        self.shopify = ShopifyPlatformAdapter()

    def analyze_keyword(self, db: Session, keyword: str, region: str = "US", category: str | None = None, user_id: int | None = None) -> dict:
        del category
        reality = asyncio.run(self._analyze_async(db=db, keyword=keyword.strip(), country=region or "US"))
        source_status = dict(reality.source_status)
        platform_signals = self._build_platform_signals(reality)
        reasoning = self._build_reasoning(reality)
        risk_level = "low" if reality.confidence_score >= 0.8 else "medium" if reality.confidence_score >= 0.6 else "high"
        commercial_context = self._authorized_commercial_context(db, user_id=user_id, keyword=keyword.strip()) if user_id else {}

        return {
            "keyword": keyword.strip(),
            "region": region,
            "category": None,
            "trend_score": round(reality.trend_score, 2),
            "trend_strength": round(reality.trend_score, 2),
            "demand_score": round(reality.demand_score, 2),
            "competition_score": round(reality.competition_pressure, 2),
            "competition": round(reality.competition_pressure, 2),
            "opportunity_score": round(reality.market_score, 2),
            "recommendation_score": round(reality.market_score, 2),
            "recommendation": reality.recommendation,
            "reasons": [
                reasoning["demand_reason"],
                reasoning["competition_reason"],
                reasoning["trend_reason"],
            ],
            "source": ",".join([f"{k}:{v}" for k, v in source_status.items()]),
            "market_score": round(reality.market_score, 2),
            "market_real_score": round(reality.market_score, 2),
            "competition_level": self._competition_level_label(reality.competition_pressure),
            "market_saturation": round(reality.competition_pressure, 2),
            "entry_barrier": self._competition_level_label(reality.competition_pressure),
            "confidence": round(reality.confidence_score, 2),
            "confidence_score": round(reality.confidence_score, 4),
            "risk_flags": reality.risk_flags,
            "risk_level": risk_level,
            "is_mock": any(status == "fallback" for status in source_status.values()),
            "mock_penalty": round(max(0.0, 1.0 - reality.real_data_ratio), 2),
            "reasoning": reasoning,
            "platform_signals": platform_signals,
            "keyword_cluster": {
                "related_keywords": [keyword.strip(), f"{keyword.strip()} review", f"{keyword.strip()} usa", f"{keyword.strip()} best"],
                "long_tail_keywords": [f"best {keyword.strip()}", f"{keyword.strip()} market", f"{keyword.strip()} demand", f"{keyword.strip()} worth buying"],
                "commercial_intent": round(reality.commercial_intent, 2),
            },
            "platform_compatibility": {
                "shopify_ready": source_status.get("shopify") == "real",
                "alibaba_match": [keyword.strip(), f"{keyword.strip()} supplier"],
                "tiktok_potential": float((platform_signals.get("tiktok") or {}).get("tiktok_trend_score") or 0),
            },
            "data_source_map": source_status,
            "data_sources": reality.signals,
            "market_signals": [
                {
                    "source": key,
                    "value": value.get("value"),
                    "confidence": value.get("confidence"),
                    "is_real": str(value.get("data_status") or "") in {"real", "limited"},
                    "api_status": value.get("data_status"),
                }
                for key, value in reality.signals.items()
            ],
            "market_growth": round(self._market_growth(reality.signals), 2),
            "market_opportunity": {
                "market_score": round(reality.market_score, 2),
                "entry_recommendation": reality.recommendation,
                "confidence": round(reality.confidence_score, 2),
                "risk_level": risk_level,
            },
            "source_status": source_status,
            "trend_direction": self._merge_trend_direction(reality.signals),
            "real_ratio": round(reality.real_data_ratio, 4),
            "partial_ratio": round(sum(1 for v in source_status.values() if v == "limited") / max(len(source_status), 1), 2),
            "mock_ratio": round(sum(1 for v in source_status.values() if v == "fallback") / max(len(source_status), 1), 4),
            "missing_credentials": [],
            "real_data_ratio": round(reality.real_data_ratio, 4),
            "profit_potential": round(reality.profit_potential, 2),
            "evidence_sources": reality.evidence_sources,
            "source_reliability": reality.source_reliability,
            "commercial_score": round(float(commercial_context.get("commercial_reality_score") or reality.commercial_score), 2),
            "commercial_reality_score": round(float(commercial_context.get("commercial_reality_score") or reality.commercial_score), 2),
            "real_sales_signal": commercial_context.get("real_sales_signal"),
            "customer_validation": commercial_context.get("customer_validation"),
            "market_fit_score": commercial_context.get("market_fit_score"),
            "repeat_purchase_signal": commercial_context.get("repeat_purchase_signal"),
            "profit_validation": commercial_context.get("profit_validation"),
            "consumer_interest": round(reality.consumer_interest, 2),
            "commercial_intent": round(reality.commercial_intent, 2),
            "competition_pressure": round(reality.competition_pressure, 2),
            "trend_stage": reality.trend_stage,
            "trend_lifecycle": reality.trend_lifecycle,
            "reality_sources": reality.reality_sources,
            "opportunity_reason": reality.opportunity_reason,
            "commercial_intent_score": round(reality.commercial_intent, 2),
            "consumer_interest_score": round(reality.consumer_interest, 2),
            "commercial_competition": round(reality.commercial_competition, 2),
            "ad_market_value": round(reality.ad_market_value, 2),
            "brand_activity": round(reality.brand_activity, 2),
            "purchase_signal": round(reality.purchase_signal, 2),
        }

    def radar_status(self, db: Session | None, keyword: str, region: str = "US") -> dict:
        del db
        reality = asyncio.run(self._analyze_async(db=None, keyword=keyword.strip(), country=region or "US"))
        return {
            "keyword": keyword.strip(),
            "country": region,
            "market_score": round(reality.market_score, 2),
            "confidence_score": round(reality.confidence_score, 4),
            "real_data_ratio": round(reality.real_data_ratio, 4),
            "sources": {
                key: {
                    "status": value,
                    "reliability": round(reality.source_reliability.get(key, 0.0), 4),
                }
                for key, value in reality.source_status.items()
            },
            "recommendation": reality.recommendation,
            "risk_flags": reality.risk_flags,
        }

    def reality_report(self, keyword: str, region: str = "US", category: str | None = None) -> dict:
        del category
        reality = asyncio.run(self._analyze_async(db=None, keyword=keyword.strip(), country=region or "US"))
        return {
            "keyword": keyword.strip(),
            "country": region,
            "market_score": round(reality.market_score, 2),
            "confidence_score": round(reality.confidence_score, 4),
            "consumer_interest": round(reality.consumer_interest, 2),
            "commercial_intent": round(reality.commercial_intent, 2),
            "commercial_score": round(reality.commercial_score, 2),
            "purchase_signal": round(reality.purchase_signal, 2),
            "ad_market_value": round(reality.ad_market_value, 2),
            "brand_activity": round(reality.brand_activity, 2),
            "commercial_competition": round(reality.commercial_competition, 2),
            "competition_pressure": round(reality.competition_pressure, 2),
            "trend_stage": reality.trend_stage,
            "trend_lifecycle": reality.trend_lifecycle,
            "real_data_ratio": round(reality.real_data_ratio, 4),
            "sources": {
                key: {
                    "status": value.get("data_status"),
                    "confidence": value.get("confidence"),
                    "signal_strength": value.get("value"),
                    "error_detail": value.get("error_detail", ""),
                }
                for key, value in reality.signals.items()
            },
            "reality_sources": reality.reality_sources,
            "recommendation": reality.recommendation,
            "risk_flags": reality.risk_flags,
            "source_reliability": reality.source_reliability,
            "reasoning": self._build_reasoning(reality),
            "opportunity_reason": reality.opportunity_reason,
        }

    def commercial_reality_report(self, db: Session | None, keyword: str, region: str = "US") -> dict:
        reality = asyncio.run(self._analyze_async(db=db, keyword=keyword.strip(), country=region or "US"))
        return {
            "keyword": keyword.strip(),
            "region": region,
            "market_score": round(reality.market_score, 2),
            "confidence": round(reality.confidence_score, 4),
            "commercial_score": round(reality.commercial_score, 2),
            "purchase_signal": round(reality.purchase_signal, 2),
            "ad_market_value": round(reality.ad_market_value, 2),
            "brand_activity": round(reality.brand_activity, 2),
            "commercial_competition": round(reality.commercial_competition, 2),
            "sources": reality.commercial_sources,
            "risks": reality.risk_flags,
            "recommendation": reality.recommendation,
        }

    async def _analyze_async(self, db: Session | None, keyword: str, country: str) -> MarketRealityReport:
        google_signal, tiktok_signal, meta_signal, amazon_signal, reddit_signal, youtube_signal, bing_signal, ebay_signal, walmart_signal, pinterest_signal = await asyncio.gather(
            self.google.fetch_signal(keyword, country),
            self.tiktok.fetch_signal(keyword, country),
            self.meta.fetch_signal(keyword, country),
            self.amazon.fetch_signal(keyword, country),
            self.reddit.fetch_signal(keyword, country),
            self.youtube.fetch_signal(keyword, country),
            self.bing.fetch_signal(keyword, country),
            self.ebay.fetch_signal(keyword, country),
            self.walmart.fetch_signal(keyword, country),
            self.pinterest.fetch_signal(keyword, country),
        )
        shopify_signal = self._shopify_signal(keyword=keyword, country=country)
        signals = {
            "google": self._with_fallback(db, keyword, country, google_signal),
            "tiktok": self._with_fallback(db, keyword, country, tiktok_signal),
            "meta": self._with_fallback(db, keyword, country, meta_signal),
            "amazon": self._with_fallback(db, keyword, country, amazon_signal),
            "reddit": self._with_fallback(db, keyword, country, reddit_signal),
            "youtube": self._with_fallback(db, keyword, country, youtube_signal),
            "bing": self._with_fallback(db, keyword, country, bing_signal),
            "ebay": self._with_fallback(db, keyword, country, ebay_signal),
            "walmart": self._with_fallback(db, keyword, country, walmart_signal),
            "pinterest": self._with_fallback(db, keyword, country, pinterest_signal),
            "shopify": shopify_signal,
        }

        keyword_cluster = keyword_intelligence_engine.analyze(keyword=keyword, related_keywords=[], rising_keywords=[])
        reality_sources = self._build_reality_sources(signals)
        commercial_snapshot = await commercial_signal_engine.analyze(
            keyword=keyword,
            region=country,
            market_signals=signals,
        )
        confidence_snapshot = market_confidence_engine.evaluate_reality(signals)

        search_signal = self._search_interest(signals)
        content_signal = self._content_interest(signals)
        discussion_signal = self._discussion_interest(signals)
        commerce_signal = self._commerce_signal(signals)
        consumer_interest = consumer_interest_engine.score(
            search_signal=search_signal,
            content_signal=content_signal,
            discussion_signal=discussion_signal,
            commerce_signal=commerce_signal,
        )
        commercial_intent = commercial_intent_engine.score(
            keyword=keyword,
            keyword_intent_score=float(keyword_cluster.get("commercial_intent") or 0),
            commerce_signal=commerce_signal,
            search_signal=search_signal,
            discussion_signal=discussion_signal,
            content_signal=content_signal,
            reality_sources=reality_sources,
        )
        purchase_signal = purchase_signal_engine.score(
            amazon_signal=float(((commercial_snapshot.sources.get("amazon_ads") or {}).get("score") or 0)),
            advertising_signal=float(commercial_snapshot.ad_market_value or 0),
            brand_signal=float(commercial_snapshot.brand_activity or 0),
            search_intent=float(commercial_intent or 0),
        )
        competition_pressure = competition_pressure_engine.score(
            amazon_signal=float((signals.get("amazon") or {}).get("value") or 0),
            ebay_signal=float((signals.get("ebay") or {}).get("value") or 0),
            walmart_signal=float((signals.get("walmart") or {}).get("value") or 0),
            result_count_proxy=float((((signals.get("bing") or {}).get("metrics") or {}).get("result_count_proxy") or 0)),
            brand_count=self._brand_count_proxy(signals),
        )
        trend_strength = self._trend_strength(signals)
        previous_record = market_reality_history_repository.latest(db, keyword=keyword, region=country) if db is not None else None
        trend_stage = trend_lifecycle_engine.classify(
            trend_strength=trend_strength,
            growth_signals=[
                float((((signals.get("google") or {}).get("metrics") or {}).get("time_change") or 0)),
                float((((signals.get("youtube") or {}).get("metrics") or {}).get("content_growth") or 0)),
                float((((signals.get("tiktok") or {}).get("metrics") or {}).get("content_growth") or 0)),
            ],
            previous_market_score=float(previous_record.market_score) if previous_record else None,
        )
        profit_potential = self._profit_potential(signals)
        market_score = round(
            max(
                0.0,
                min(
                    100.0,
                    consumer_interest * 0.25
                    + commercial_intent * 0.2
                    + purchase_signal * 0.25
                    + float(commercial_snapshot.ad_market_value) * 0.15
                    + float(commercial_snapshot.brand_activity) * 0.15,
                ),
            ),
            2,
        )
        recommendation = self._recommendation(market_score=market_score, confidence_score=confidence_snapshot.confidence_score)
        opportunity_reason = (
            f"{keyword} 在 {country} 的消费者兴趣 {round(consumer_interest, 2)}，商业意图 {round(commercial_intent, 2)}，"
            f"购买信号 {round(purchase_signal, 2)}，广告商业值 {round(commercial_snapshot.ad_market_value, 2)}，"
            f"品牌活跃度 {round(commercial_snapshot.brand_activity, 2)}，竞争压力 {round(competition_pressure, 2)}，"
            f"趋势阶段 {trend_stage}，因此建议 {recommendation}。"
        )
        risk_flags = list(confidence_snapshot.risk_flags) + list(commercial_snapshot.risks)
        if competition_pressure >= 70:
            risk_flags.append("high_competition")
        if consumer_interest < 55:
            risk_flags.append("low_consumer_interest")
        if commercial_intent < 55:
            risk_flags.append("low_commercial_intent")
        if purchase_signal < 50:
            risk_flags.append("low_purchase_signal")

        if db is not None:
            for source_name, payload in signals.items():
                self._record_source_history(db, keyword, country, source_name, payload)
            for source_name, payload in commercial_snapshot.sources.items():
                self._record_commercial_history(db, keyword, country, source_name, payload)
            market_reality_history_repository.create(
                db,
                keyword=keyword,
                region=country,
                market_score=market_score,
                confidence_score=confidence_snapshot.confidence_score,
                consumer_interest=consumer_interest,
                commercial_intent=commercial_intent,
                competition_pressure=competition_pressure,
                trend_stage=trend_stage,
                sources=reality_sources,
            )

        return MarketRealityReport(
            market_score=market_score,
            demand_score=consumer_interest,
            trend_score=trend_strength,
            competition_score=competition_pressure,
            profit_potential=profit_potential,
            real_data_ratio=confidence_snapshot.real_data_ratio,
            confidence_score=confidence_snapshot.confidence_score,
            evidence_sources=confidence_snapshot.evidence_sources,
            source_reliability=confidence_snapshot.source_reliability,
            risk_flags=sorted(set(risk_flags)),
            recommendation=recommendation,
            source_status={key: str(value.get("data_status") or "fallback") for key, value in signals.items()},
            signals=signals,
            consumer_interest=consumer_interest,
            commercial_intent=commercial_intent,
            competition_pressure=competition_pressure,
            trend_stage=trend_stage,
            trend_lifecycle=trend_stage,
            commercial_signal=commerce_signal,
            commercial_score=commercial_snapshot.commercial_score,
            commercial_competition=commercial_snapshot.commercial_competition,
            ad_market_value=commercial_snapshot.ad_market_value,
            brand_activity=commercial_snapshot.brand_activity,
            purchase_signal=purchase_signal,
            commercial_source_status={key: str(value.get("status") or "fallback") for key, value in commercial_snapshot.sources.items()},
            commercial_sources=commercial_snapshot.sources,
            reality_sources=reality_sources,
            opportunity_reason=opportunity_reason,
        )

    def _record_source_history(self, db: Session, keyword: str, country: str, source_name: str, payload: dict) -> None:
        latest = market_signal_history_repository.latest(db, keyword=keyword, region=country, source=source_name)
        previous_score = float(latest.score) if latest else 0.0
        current_value = float(payload.get("value") or 0)
        change_rate = round(((current_value - previous_score) / previous_score) * 100, 2) if previous_score else 0.0
        market_signal_history_repository.create(
            db,
            keyword=keyword,
            region=country,
            source=source_name,
            score=current_value,
            trend=current_value,
            status=str(payload.get("data_status") or "fallback"),
            confidence=float(payload.get("confidence") or 0),
            signal_strength=current_value,
            change_rate=change_rate,
        )

    def _with_fallback(self, db: Session | None, keyword: str, country: str, signal: MarketSignal) -> dict:
        payload = signal.model_dump(mode="json")
        latest = market_signal_history_repository.latest(db, keyword=keyword, region=country, source=signal.source) if db is not None else None
        if payload["data_status"] in {"real", "limited", "partial", "not_configured"}:
            return payload
        if latest:
            payload["value"] = float(latest.score)
            payload["confidence"] = max(0.2, float(payload.get("confidence") or 0) * 0.7)
            payload["data_status"] = "fallback"
            payload["is_mock"] = False
        return payload

    def _record_commercial_history(self, db: Session, keyword: str, country: str, source_name: str, payload: dict) -> None:
        commercial_signal_history_repository.create(
            db,
            keyword=keyword,
            region=country,
            source=source_name,
            signal_score=float(payload.get("score") or 0),
            status=str(payload.get("status") or "fallback"),
            reliability=float(payload.get("reliability") or 0),
        )

    def _shopify_signal(self, keyword: str, country: str) -> dict:
        products = self.shopify.search_product(keyword)
        if isinstance(products, list) and products and not products[0].get("error"):
            prices = [float(item.get("price") or 0) for item in products if str(item.get("price") or "").strip()]
            value = min(100.0, 25 + len(products) * 12)
            return {
                "source": "shopify",
                "keyword": keyword,
                "country": country,
                "signal_type": "commerce",
                "value": round(value, 2),
                "trend": "up" if len(products) >= 1 else "flat",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "confidence": 0.75,
                "is_mock": False,
                "data_status": "real",
                "metrics": {
                    "store_activity": round(value, 2),
                    "category_growth": round(max(0.0, value - 25), 2),
                    "price_band": {
                        "min": round(min(prices), 2) if prices else 0.0,
                        "max": round(max(prices), 2) if prices else 0.0,
                        "average": round(mean(prices), 2) if prices else 0.0,
                    },
                },
                "error_detail": "",
            }
        return {
            "source": "shopify",
            "keyword": keyword,
            "country": country,
            "signal_type": "commerce",
            "value": 0.0,
            "trend": "flat",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence": 0.2,
            "is_mock": False,
            "data_status": "fallback",
            "metrics": {},
            "error_detail": str(products[0].get("error") if isinstance(products, list) and products else "shopify unavailable"),
        }

    def _search_interest(self, signals: dict[str, dict]) -> float:
        google = float((signals.get("google") or {}).get("value") or 0)
        bing = float((signals.get("bing") or {}).get("value") or 0)
        return round(max(google, bing * 0.95), 2)

    def _content_interest(self, signals: dict[str, dict]) -> float:
        youtube = float((signals.get("youtube") or {}).get("value") or 0)
        youtube_growth = float((((signals.get("youtube") or {}).get("metrics") or {}).get("content_growth") or 0))
        tiktok = float((signals.get("tiktok") or {}).get("value") or 0)
        pinterest = float((signals.get("pinterest") or {}).get("value") or 0)
        score = max(youtube, tiktok, pinterest) * 0.75 + mean([youtube_growth, tiktok, max(pinterest, 20.0)]) * 0.25
        return round(max(0.0, min(100.0, score + 12)), 2)

    def _discussion_interest(self, signals: dict[str, dict]) -> float:
        reddit = float((signals.get("reddit") or {}).get("value") or 0)
        if str((signals.get("reddit") or {}).get("data_status") or "") == "limited":
            reddit += 8
        return round(max(0.0, min(100.0, reddit)), 2)

    def _commerce_signal(self, signals: dict[str, dict]) -> float:
        values: list[float] = []
        for source_name in ["amazon", "walmart", "ebay", "shopify"]:
            payload = signals.get(source_name) or {}
            status = str(payload.get("data_status") or "fallback")
            value = float(payload.get("value") or 0)
            if status in {"real", "limited", "partial"} and value > 0:
                values.append(value)
        if not values:
            return 0.0
        return round(max(0.0, min(100.0, mean(values) + 8)), 2)

    def _trend_strength(self, signals: dict[str, dict]) -> float:
        directional_bonus = 0.0
        for source_name in ["bing", "youtube", "amazon", "walmart", "tiktok", "reddit"]:
            if str((signals.get(source_name) or {}).get("trend") or "") == "up":
                directional_bonus += 4
        score = (
            self._search_interest(signals) * 0.35
            + self._content_interest(signals) * 0.25
            + self._commerce_signal(signals) * 0.2
            + self._discussion_interest(signals) * 0.2
        ) + directional_bonus
        return round(max(0.0, min(100.0, score)), 2)

    def _brand_count_proxy(self, signals: dict[str, dict]) -> float:
        amazon_rank = float((((signals.get("amazon") or {}).get("metrics") or {}).get("category_rank") or 0))
        ebay_listings = float((((signals.get("ebay") or {}).get("metrics") or {}).get("listing_count") or 0))
        walmart_count = float((((signals.get("walmart") or {}).get("metrics") or {}).get("product_count") or 0))
        return round((amazon_rank / 4) + (ebay_listings / 6) + (walmart_count / 20), 2)

    def _profit_potential(self, signals: dict[str, dict]) -> float:
        amazon_prices = (((signals.get("amazon") or {}).get("metrics") or {}).get("price_range") or {})
        ebay_prices = (((signals.get("ebay") or {}).get("metrics") or {}).get("price_range") or {})
        walmart_prices = (((signals.get("walmart") or {}).get("metrics") or {}).get("price_range") or {})
        averages = [float(item.get("average") or 0) for item in [amazon_prices, ebay_prices, walmart_prices] if float(item.get("average") or 0) > 0]
        if not averages:
            return 0.0
        avg_price = mean(averages)
        return round(max(0.0, min(100.0, 25 + avg_price / 3)), 2)

    def _build_reality_sources(self, signals: dict[str, dict]) -> list[dict]:
        sources: list[dict] = []
        for source_name, payload in signals.items():
            model = MarketRealitySignal(
                source_name=source_name,
                signal_type=str(payload.get("signal_type") or "unknown"),
                value=float(payload.get("value") or 0),
                reliability=float(payload.get("confidence") or 0),
                timestamp=str(payload.get("timestamp") or ""),
                is_real=str(payload.get("data_status") or "") in {"real", "limited"},
                status=str(payload.get("data_status") or "fallback"),
                metadata=dict(payload.get("metrics") or {}),
            )
            sources.append(
                {
                    "source": model.source_name,
                    "status": model.status,
                    "reliability": round(model.reliability, 4),
                }
            )
        return sources

    def _competition_level_label(self, competition_score: float) -> str:
        if competition_score >= 72:
            return "high"
        if competition_score >= 45:
            return "medium"
        return "low"

    def _merge_trend_direction(self, signals: dict[str, dict]) -> str:
        values = [str(item.get("trend") or "flat") for item in signals.values()]
        if values.count("up") >= 4:
            return "up"
        if values.count("down") >= 3:
            return "down"
        return "flat"

    def _market_growth(self, signals: dict[str, dict]) -> float:
        return mean([float(item.get("value") or 0) for item in signals.values() if str(item.get("trend") or "") == "up"] or [0.0])

    def _recommendation(self, *, market_score: float, confidence_score: float) -> str:
        if confidence_score < 0.6:
            return "WATCH"
        if market_score >= 75 and confidence_score >= 0.8:
            return "BUY"
        if market_score >= 60 and confidence_score >= 0.7:
            return "TEST"
        if market_score >= 40:
            return "WATCH"
        return "IGNORE"

    def _build_platform_signals(self, reality: MarketRealityReport) -> dict:
        return {
            source: ((payload.get("metrics") or {}) if source != "amazon" else {
                **((payload.get("metrics") or {})),
                "demand_score": float(payload.get("value") or 0),
                "competition_density": round(reality.competition_pressure, 2),
            })
            for source, payload in reality.signals.items()
        }

    def _build_reasoning(self, reality: MarketRealityReport) -> dict:
        return {
            "demand_reason": f"消费者兴趣 {reality.consumer_interest}，由搜索、内容、讨论、成交四层信号综合得出。",
            "competition_reason": f"竞争压力 {reality.competition_pressure}，综合 Amazon、eBay、Walmart 和搜索结果压力判断。",
            "trend_reason": f"市场分 {reality.market_score}，购买信号 {reality.purchase_signal}，广告商业值 {reality.ad_market_value}，品牌活跃度 {reality.brand_activity}，当前建议 {reality.recommendation}。",
        }

    def _authorized_commercial_context(self, db: Session, *, user_id: int | None, keyword: str) -> dict:
        if not user_id:
            return {}
        try:
            from app.core.commercial_data_connection_engine import commercial_data_connection_engine

            signal = commercial_data_connection_engine._shopify_commercial_signal(db, user_id=user_id, keyword=keyword)
            if not signal.get("connected"):
                return {}
            return signal
        except Exception:
            return {}


market_intelligence_engine = MarketIntelligenceEngine()
