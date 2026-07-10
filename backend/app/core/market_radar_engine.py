from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from statistics import mean

from sqlalchemy.orm import Session

from app.adapters.market.amazon.amazon_market_provider import AmazonMarketProvider
from app.adapters.market.google.google_trends_provider import GoogleTrendsProvider
from app.adapters.market.shopify.shopify_market_provider import ShopifyMarketProvider
from app.adapters.market.tiktok.tiktok_market_provider import TikTokMarketProvider
from app.core.keyword_intelligence_engine import keyword_intelligence_engine
from app.repositories.market_analysis_history import market_analysis_history_repository
from app.repositories.amazon_market_history import amazon_market_history_repository
from app.repositories.market_signal_history import market_signal_history_repository


class MarketRadarEngine:
    def __init__(self) -> None:
        self.google = GoogleTrendsProvider()
        self.amazon = AmazonMarketProvider()
        self.tiktok = TikTokMarketProvider()
        self.shopify = ShopifyMarketProvider()

    def analyze(
        self,
        *,
        db: Session | None,
        keyword: str,
        region: str = "global",
        category: str | None = None,
        time_range: str = "90d",
    ) -> dict:
        return asyncio.run(
            self.analyze_async(
                db=db,
                keyword=keyword,
                region=region,
                category=category,
                time_range=time_range,
            )
        )

    async def analyze_async(
        self,
        *,
        db: Session | None,
        keyword: str,
        region: str = "global",
        category: str | None = None,
        time_range: str = "90d",
    ) -> dict:
        normalized_keyword = str(keyword or "").strip()
        google_raw, amazon_raw, tiktok_raw, shopify_raw = await asyncio.gather(
            self.google.fetch_market_signal(normalized_keyword, region, category, time_range),
            self.amazon.fetch_market_signal(normalized_keyword, region, category, time_range),
            self.tiktok.fetch_market_signal(normalized_keyword, region, category, time_range),
            self.shopify.fetch_market_signal(normalized_keyword, region, category, time_range),
        )
        providers = {
            "google": google_raw,
            "amazon": amazon_raw,
            "tiktok": tiktok_raw,
            "shopify": shopify_raw,
        }
        providers = self._apply_cache_if_needed(db=db, keyword=normalized_keyword, region=region, providers=providers)
        amazon_growth = (
            amazon_market_history_repository.growth_windows(db, keyword=normalized_keyword, marketplace=region)
            if db is not None else {"7d": 0.0, "30d": 0.0, "90d": 0.0}
        )

        google_signal = providers["google"]["signal"]
        amazon_signal = providers["amazon"]["signal"]
        tiktok_signal = providers["tiktok"]["signal"]
        shopify_signal = providers["shopify"]["signal"]
        keyword_cluster = keyword_intelligence_engine.analyze(
            keyword=normalized_keyword,
            related_keywords=google_signal.get("related_queries"),
            rising_keywords=google_signal.get("rising_queries"),
        )
        demand_score = self._weighted_average(
            [
                (float(google_signal.get("interest_score") or 0), self._weight_for_status(providers["google"]["source_status"], 0.35)),
                (float(amazon_signal.get("demand_score") or 0), self._weight_for_status(providers["amazon"]["source_status"], 0.40)),
                (float(tiktok_signal.get("trend_score") or 0), self._weight_for_status(providers["tiktok"]["source_status"], 0.15)),
                (float(shopify_signal.get("category_activity") or 0), self._weight_for_status(providers["shopify"]["source_status"], 0.10)),
            ]
        )
        trend_strength = self._weighted_average(
            [
                (50 + float(google_signal.get("growth_rate") or 0), self._weight_for_status(providers["google"]["source_status"], 0.45)),
                (float(tiktok_signal.get("trend_score") or 0), self._weight_for_status(providers["tiktok"]["source_status"], 0.35)),
                (50 + float(shopify_signal.get("market_growth") or 0) / 2, self._weight_for_status(providers["shopify"]["source_status"], 0.20)),
            ]
        )
        competition_score = self._weighted_average(
            [
                (float(amazon_signal.get("competition_density") or 0), self._weight_for_status(providers["amazon"]["source_status"], 0.65)),
                (float(shopify_signal.get("store_density") or 0), self._weight_for_status(providers["shopify"]["source_status"], 0.35)),
            ]
        )
        competition_level = self._band(competition_score, 35, 70)
        profit_potential = self._estimate_profit_potential(amazon_signal=amazon_signal, shopify_signal=shopify_signal)
        commercial_intent = float(keyword_cluster.get("commercial_intent") or 0)
        competition_penalty = self._competition_penalty(competition_score, competition_level)
        market_score = max(
            0.0,
            min(
                100.0,
                (demand_score * 0.35)
                + (trend_strength * 0.25)
                + (commercial_intent * 0.20)
                + (profit_potential * 0.20)
                - competition_penalty,
            ),
        )
        confidence = round(mean([float(item.get("confidence") or 0) for item in providers.values()]), 2)
        real_ratio = round(
            sum(1 for item in providers.values() if item.get("source_status") in {"real", "verified"}) / max(len(providers), 1),
            2,
        )
        partial_ratio = round(
            sum(1 for item in providers.values() if item.get("source_status") in {"partial", "cached"}) / max(len(providers), 1),
            2,
        )
        mock_ratio = round(sum(1 for item in providers.values() if bool(item.get("is_mock"))) / max(len(providers), 1), 2)
        trend_direction = str(google_signal.get("trend_direction") or "flat")
        recommendation = self._recommendation(market_score)
        risk_level = self._risk_level(confidence=confidence, competition_score=competition_score, real_ratio=real_ratio)
        market_opportunity = {
            "market_score": round(market_score, 2),
            "entry_recommendation": recommendation,
            "confidence": confidence,
            "risk_level": risk_level,
            "reasoning": [
                f"需求分 {round(demand_score, 2)}，趋势分 {round(trend_strength, 2)}，商业意图 {round(commercial_intent, 2)}。",
                f"竞争分 {round(competition_score, 2)}，利润潜力 {round(profit_potential, 2)}。",
                f"真实比例 {real_ratio}，partial 比例 {partial_ratio}，mock 比例 {mock_ratio}。",
            ],
        }
        previous_record = (
            market_analysis_history_repository.latest_for_keyword(db, keyword=normalized_keyword, region=region)
            if db is not None else None
        )
        risk_flags: list[str] = []
        if confidence < 0.35:
            risk_flags.append("low_confidence")
        if competition_score >= 70:
            risk_flags.append("high_competition")
        if trend_strength <= 35:
            risk_flags.append("weak_trend")
        if partial_ratio > 0:
            risk_flags.append("partial_data_used")
        if mock_ratio > 0:
            risk_flags.append("mock_data_used")

        payload = {
            "keyword": normalized_keyword,
            "region": region,
            "category": category,
            "market_score": round(market_score, 2),
            "demand_score": round(demand_score, 2),
            "trend_score": round(trend_strength, 2),
            "trend_strength": round(trend_strength, 2),
            "competition_score": round(competition_score, 2),
            "competition": round(competition_score, 2),
            "competition_level": competition_level,
            "trend_direction": trend_direction,
            "keyword_cluster": keyword_cluster,
            "source_status": {key: value.get("source_status") for key, value in providers.items()},
            "confidence": confidence,
            "recommendation": recommendation,
            "market_opportunity": market_opportunity,
            "risk_level": risk_level,
            "risk_flags": risk_flags,
            "data_sources": providers,
            "platform_signals": {
                "google": google_signal,
                "amazon": {**amazon_signal, "growth_windows": amazon_growth},
                "tiktok": tiktok_signal,
                "shopify": shopify_signal,
            },
            "is_mock": any(bool(item.get("is_mock")) for item in providers.values()),
            "real_ratio": real_ratio,
            "partial_ratio": partial_ratio,
            "mock_ratio": mock_ratio,
            "reasoning": {
                "demand_reason": f"需求分来自 Google / Amazon / TikTok / Shopify 汇总，当前为 {round(demand_score, 2)}。",
                "competition_reason": f"竞争强度为 {competition_level}，竞争分 {round(competition_score, 2)}。",
                "trend_reason": f"趋势方向 {trend_direction}，趋势强度 {round(trend_strength, 2)}。",
            },
            "trend_points": google_signal.get("trend_points") or [],
            "market_growth": round(float(google_signal.get("growth_rate") or 0), 2),
            "previous_score": float(previous_record.score) if previous_record else None,
        }
        if db is not None:
            self._persist_source_history(
                db=db,
                keyword=normalized_keyword,
                region=region,
                providers=providers,
            )
            amazon_market_history_repository.create_signal_snapshot(
                db,
                keyword=normalized_keyword,
                marketplace=region,
                signal=amazon_signal,
                status=str(providers["amazon"].get("source_status") or "unavailable"),
                confidence=float(providers["amazon"].get("confidence") or 0),
                timestamp=str(providers["amazon"].get("timestamp") or ""),
            )
            amazon_market_history_repository.create_history_point(
                db,
                keyword=normalized_keyword,
                marketplace=region,
                signal=amazon_signal,
                captured_at=datetime.now(UTC),
            )
        return payload

    def _apply_cache_if_needed(self, *, db: Session | None, keyword: str, region: str, providers: dict[str, dict]) -> dict[str, dict]:
        if db is None:
            return providers
        for source_name, payload in providers.items():
            if payload.get("source_status") != "unavailable":
                continue
            latest = market_signal_history_repository.latest(db, keyword=keyword, region=region, source=source_name)
            if not latest:
                continue
            providers[source_name] = {
                **payload,
                "source_status": "cached",
                "confidence": 0.35,
                "signal": {
                    **payload.get("signal", {}),
                    "status": "cached",
                    "cached_score": latest.score,
                    "cached_trend": latest.trend,
                },
            }
            if source_name == "google":
                providers[source_name]["signal"]["interest_score"] = latest.score
                providers[source_name]["signal"]["growth_rate"] = latest.trend
                providers[source_name]["signal"]["trend_direction"] = "up" if latest.trend > 0 else "down" if latest.trend < 0 else "flat"
            elif source_name == "amazon":
                providers[source_name]["signal"]["demand_score"] = latest.score
                providers[source_name]["signal"]["competition_density"] = max(0.0, 100.0 - latest.trend)
            elif source_name == "tiktok":
                providers[source_name]["signal"]["trend_score"] = latest.score
                providers[source_name]["signal"]["content_growth"] = latest.trend
            elif source_name == "shopify":
                providers[source_name]["signal"]["category_activity"] = latest.score
                providers[source_name]["signal"]["market_growth"] = latest.trend
        return providers

    def _persist_source_history(self, *, db: Session, keyword: str, region: str, providers: dict[str, dict]) -> None:
        for source_name, payload in providers.items():
            signal = payload.get("signal") or {}
            score, trend = self._source_score(source_name, signal)
            market_signal_history_repository.create(
                db,
                keyword=keyword,
                region=region,
                source=source_name,
                score=score,
                trend=trend,
                status=str(payload.get("source_status") or "unknown"),
            )

    def _source_score(self, source_name: str, signal: dict) -> tuple[float, float]:
        if source_name == "google":
            return float(signal.get("interest_score") or 0), float(signal.get("growth_rate") or 0)
        if source_name == "amazon":
            return float(signal.get("demand_score") or 0), max(0.0, 100.0 - float(signal.get("competition_density") or 0))
        if source_name == "tiktok":
            return float(signal.get("trend_score") or 0), float(signal.get("content_growth") or 0)
        return float(signal.get("category_activity") or 0), float(signal.get("market_growth") or 0)

    def _weight_for_status(self, status: str, default_weight: float) -> float:
        normalized = str(status or "").lower()
        if normalized in {"real", "verified"}:
            return default_weight
        if normalized in {"partial", "cached"}:
            return default_weight * 0.6
        if normalized == "mock":
            return default_weight * 0.3
        return 0.0

    def _weighted_average(self, values: list[tuple[float, float]]) -> float:
        active = [(value, weight) for value, weight in values if weight > 0]
        if not active:
            return 0.0
        total_weight = sum(weight for _, weight in active)
        return round(sum(value * weight for value, weight in active) / total_weight, 2)

    def _estimate_profit_potential(self, *, amazon_signal: dict, shopify_signal: dict) -> float:
        amazon_avg = float((amazon_signal.get("price_range") or {}).get("average") or 0)
        shopify_avg = float((shopify_signal.get("price_range") or {}).get("average") or 0)
        anchor = max(amazon_avg, shopify_avg)
        if anchor <= 0:
            return 25.0
        return round(max(0.0, min(100.0, 20 + anchor * 1.2)), 2)

    def _competition_penalty(self, competition_score: float, competition_level: str) -> float:
        level_penalty = {"low": 8.0, "medium": 15.0, "high": 25.0}.get(competition_level, 15.0)
        return round((competition_score * 0.18) + level_penalty, 2)

    def _band(self, value: float, low_cut: float, high_cut: float) -> str:
        if value >= high_cut:
            return "high"
        if value >= low_cut:
            return "medium"
        return "low"

    def _recommendation(self, market_score: float) -> str:
        if market_score >= 75:
            return "BUY"
        if market_score >= 55:
            return "TEST"
        if market_score >= 35:
            return "WATCH"
        return "IGNORE"

    def _risk_level(self, *, confidence: float, competition_score: float, real_ratio: float) -> str:
        if confidence >= 0.7 and competition_score < 55 and real_ratio >= 0.5:
            return "low"
        if confidence >= 0.4 and competition_score < 75:
            return "medium"
        return "high"


market_radar_engine = MarketRadarEngine()
