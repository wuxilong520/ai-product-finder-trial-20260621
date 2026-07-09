from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.market_radar_engine import market_radar_engine
from app.repositories.market_analysis_history import market_analysis_history_repository
from app.repositories.market_intelligence import market_intelligence_repository


class MarketIntelligenceEngine:
    def analyze_keyword(self, db: Session, keyword: str, region: str = "global", category: str | None = None) -> dict:
        radar = market_radar_engine.analyze(
            db=db,
            keyword=keyword,
            region=region,
            category=category,
        )
        recommendation = str(radar["recommendation"])
        market_confidence = float(radar["confidence"])
        reasons = [
            str(radar["reasoning"]["demand_reason"]),
            str(radar["reasoning"]["competition_reason"]),
            f"{radar['reasoning']['trend_reason']} 市场机会推荐 {radar['market_opportunity']['entry_recommendation']}，市场分 {radar['market_score']}。",
        ]
        source_label = ",".join([f"{key}:{value}" for key, value in (radar.get("source_status") or {}).items()])
        payload = {
            "keyword": keyword.strip(),
            "region": region,
            "category": category,
            "trend_score": round(float(radar["trend_score"]), 2),
            "trend_strength": round(float(radar["trend_strength"]), 2),
            "demand_score": round(float(radar["demand_score"]), 2),
            "competition_score": round(float(radar["competition_score"]), 2),
            "competition": round(float(radar["competition"]), 2),
            "opportunity_score": round(float(radar["market_opportunity"]["market_score"]), 2),
            "recommendation_score": round(float(radar["market_opportunity"]["market_score"]), 2),
            "recommendation": recommendation,
            "reasons": reasons,
            "source": source_label or "market_intelligence_engine",
            "market_score": round(float(radar["market_score"]), 2),
            "competition_level": radar["competition_level"],
            "market_saturation": round(float(radar["competition_score"]), 2),
            "entry_barrier": radar["competition_level"],
            "confidence": round(float(market_confidence), 2),
            "risk_flags": radar["risk_flags"],
            "risk_level": radar["risk_level"],
            "is_mock": bool(radar["is_mock"]),
            "mock_penalty": round(float(radar["mock_ratio"]), 2),
            "reasoning": radar["reasoning"],
            "platform_signals": radar["platform_signals"],
            "keyword_cluster": radar["keyword_cluster"],
            "platform_compatibility": {
                "shopify_ready": (radar["source_status"].get("shopify") in {"real", "partial"}),
                "alibaba_match": [
                    keyword.strip(),
                    f"{keyword.strip()} wholesale",
                    f"{keyword.strip()} supplier",
                ],
                "tiktok_potential": float((radar["platform_signals"].get("tiktok") or {}).get("trend_score") or 0),
            },
            "data_source_map": radar["source_status"],
            "data_sources": radar["data_sources"],
            "market_signals": [],
            "market_growth": radar["market_growth"],
            "market_opportunity": radar["market_opportunity"],
            "source_status": radar["source_status"],
            "trend_direction": radar["trend_direction"],
            "real_ratio": radar["real_ratio"],
            "partial_ratio": radar["partial_ratio"],
            "mock_ratio": radar["mock_ratio"],
        }
        change_rate = None
        if radar["previous_score"] and float(radar["previous_score"]) != 0:
            change_rate = round(((payload["market_score"] - float(radar["previous_score"])) / float(radar["previous_score"])) * 100, 2)
            if change_rate > 20:
                payload["risk_flags"] = sorted(set([*payload["risk_flags"], "RISING_OPPORTUNITY"]))
            elif change_rate < -20:
                payload["risk_flags"] = sorted(set([*payload["risk_flags"], "DECLINING"]))
        market_intelligence_repository.create(
            db,
            keyword=keyword.strip(),
            category=category,
            trend_score=payload["trend_score"],
            demand_score=payload["demand_score"],
            competition_score=payload["competition_score"],
            opportunity_score=payload["opportunity_score"],
            recommendation_score=payload["recommendation_score"],
            recommendation=payload["recommendation"],
            reasons=payload["reasons"],
            source=payload["source"],
        )
        market_analysis_history_repository.create(
            db,
            keyword=keyword.strip(),
            region=region,
            category=category,
            score=payload["market_score"],
            trend=payload["trend_score"],
            competition=payload["competition_score"],
            source=payload["source"],
            confidence=payload["confidence"],
            is_mock=payload["is_mock"],
            previous_score=float(radar["previous_score"]) if radar["previous_score"] else None,
            current_score=payload["market_score"],
            change_rate=change_rate,
            trend_direction=payload["trend_direction"],
            snapshot=payload,
        )
        return payload


market_intelligence_engine = MarketIntelligenceEngine()
