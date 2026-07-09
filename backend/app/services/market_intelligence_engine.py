from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.market_signal_engine import market_signal_engine
from app.core.market_opportunity_model import market_opportunity_model
from app.core.market_intelligence_engine import MarketQuery, market_intelligence_engine as core_market_intelligence_engine
from app.repositories.market_analysis_history import market_analysis_history_repository
from app.repositories.market_intelligence import market_intelligence_repository


class MarketIntelligenceEngine:
    def analyze_keyword(self, db: Session, keyword: str, region: str = "global", category: str | None = None) -> dict:
        result = core_market_intelligence_engine.analyze(
            MarketQuery(keyword=keyword, region=region, category=category)
        )
        intelligence = result.market_intelligence
        signal_bundle = market_signal_engine.build(
            keyword=keyword.strip(),
            region=region,
            data_sources=intelligence.data_sources,
            market_intelligence=intelligence.model_dump(mode="json"),
            db=db,
        )
        market_opportunity = market_opportunity_model.evaluate(
            demand_score=signal_bundle["demand_score"],
            trend_score=signal_bundle["trend_score"],
            competition_score=signal_bundle["competition_score"],
            platform_compatibility=intelligence.platform_compatibility.model_dump(mode="json"),
        )
        intelligence = intelligence.model_copy(
            update={
                "market_signals": signal_bundle["market_signals"],
                "market_growth": signal_bundle["market_growth"],
                "trend_direction": signal_bundle["trend_direction"],
                "market_opportunity": market_opportunity.model_dump(mode="json"),
                "source_status": signal_bundle["source_status"],
                "confidence": min(float(signal_bundle["confidence"]), 0.3) if signal_bundle["all_mock"] else float(signal_bundle["confidence"]),
                "all_sources_mock": signal_bundle["all_mock"],
            }
        )
        recommendation = market_opportunity.recommendation
        market_confidence = float(intelligence.confidence)
        reasons = [
            result.reasoning["demand_reason"],
            result.reasoning["competition_reason"],
            f"{result.reasoning['trend_reason']} 市场机会等级 {market_opportunity.level}，机会分 {market_opportunity.score}。",
        ]
        source_label = ",".join(
            sorted(
                {
                    str(item.get("source") or "")
                    for item in intelligence.data_sources.values()
                }
            )
        )
        payload = {
            "keyword": keyword.strip(),
            "region": region,
            "category": category,
            "trend_score": round(float(intelligence.trend_strength), 2),
            "demand_score": round(float(signal_bundle["demand_score"]), 2),
            "competition_score": round(float(signal_bundle["competition_score"]), 2),
            "opportunity_score": round(float(market_opportunity.score), 2),
            "recommendation_score": round(float(market_opportunity.score), 2),
            "recommendation": recommendation,
            "reasons": reasons,
            "source": source_label or "market_intelligence_engine",
            "market_score": round(float(result.market_score), 2),
            "competition_level": intelligence.competition_level,
            "market_saturation": round(float(intelligence.market_saturation), 2),
            "entry_barrier": intelligence.entry_barrier,
            "confidence": round(float(market_confidence), 2),
            "risk_flags": result.risk_flags,
            "is_mock": intelligence.is_mock,
            "mock_penalty": round(float(intelligence.mock_penalty), 2),
            "reasoning": result.reasoning,
            "platform_signals": intelligence.platform_signals.model_dump(mode="json"),
            "keyword_cluster": intelligence.keyword_cluster.model_dump(mode="json"),
            "platform_compatibility": intelligence.platform_compatibility.model_dump(mode="json"),
            "data_source_map": intelligence.data_source_map,
            "data_sources": intelligence.data_sources,
            "market_signals": intelligence.market_signals,
            "market_growth": intelligence.market_growth,
            "market_opportunity": intelligence.market_opportunity,
            "source_status": intelligence.source_status,
            "trend_direction": intelligence.trend_direction,
        }
        if signal_bundle["all_mock"]:
            payload["confidence"] = min(float(payload["confidence"]), 0.3)
            payload["recommendation"] = "IGNORE" if payload["recommendation"] == "BUY" else payload["recommendation"]
            payload["risk_flags"] = sorted(set([*payload["risk_flags"], "all_sources_mock"]))

        change_rate = None
        if signal_bundle["previous_record"] and float(signal_bundle["previous_record"].score or 0) != 0:
            change_rate = round(((payload["market_score"] - float(signal_bundle["previous_record"].score)) / float(signal_bundle["previous_record"].score)) * 100, 2)
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
            previous_score=float(signal_bundle["previous_record"].score) if signal_bundle["previous_record"] else None,
            current_score=payload["market_score"],
            change_rate=change_rate,
            trend_direction=signal_bundle["trend_direction"],
            snapshot=payload,
        )
        return payload


market_intelligence_engine = MarketIntelligenceEngine()
