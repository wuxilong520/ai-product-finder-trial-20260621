from __future__ import annotations

from statistics import mean

from sqlalchemy.orm import Session

from app.repositories.market_intelligence import market_intelligence_repository
from app.services.data_hub import data_hub


class MarketIntelligenceEngine:
    def analyze_keyword(self, db: Session, keyword: str) -> dict:
        normalized_keyword = keyword.strip()
        signals = data_hub.get_market_data(db, keyword=normalized_keyword)
        payload = self._build_payload(normalized_keyword, signals)
        market_intelligence_repository.create(db, keyword=normalized_keyword, **payload)
        return payload

    def _build_payload(self, keyword: str, signals: list) -> dict:
        if not signals:
            trend_score = 0.0
            demand_score = 0.0
            competition_score = 0.0
            category = None
            source = "data_hub_empty"
            confidence_score = 0.0
        else:
            trend_score = mean(item.trend_score for item in signals)
            demand_score = mean(item.demand_level for item in signals)
            competition_score = mean(item.competition_index for item in signals)
            category = next((item.category for item in signals if item.category), None)
            source = ",".join(sorted({item.source_platform for item in signals}))
            confidence_score = mean(item.confidence_score for item in signals)

        opportunity_score = self._clamp(
            trend_score * 0.34
            + demand_score * 0.34
            + (100 - competition_score) * 0.20
            + confidence_score * 0.12
        )
        recommendation_score = self._clamp(
            trend_score * 0.25
            + demand_score * 0.3
            + (100 - competition_score) * 0.2
            + opportunity_score * 0.25
        )
        recommendation = self._recommendation(recommendation_score, competition_score)
        reasons = self._reasons(
            keyword=keyword,
            signal_count=len(signals),
            trend_score=trend_score,
            demand_score=demand_score,
            competition_score=competition_score,
            opportunity_score=opportunity_score,
            confidence_score=confidence_score,
        )

        return {
            "category": category,
            "trend_score": round(trend_score, 2),
            "demand_score": round(demand_score, 2),
            "competition_score": round(competition_score, 2),
            "opportunity_score": round(opportunity_score, 2),
            "recommendation_score": round(recommendation_score, 2),
            "recommendation": recommendation,
            "reasons": reasons,
            "source": source,
        }

    def _reasons(
        self,
        *,
        keyword: str,
        signal_count: int,
        trend_score: float,
        demand_score: float,
        competition_score: float,
        opportunity_score: float,
        confidence_score: float,
    ) -> list[str]:
        reasons: list[str] = []
        if signal_count > 0:
            reasons.append(f"关键词“{keyword}”当前已经通过统一数据协议层完成标准化聚合。")
        else:
            reasons.append(f"当前还没有拿到足够的“{keyword}”市场信号，本次按保守逻辑输出。")

        if trend_score >= 65:
            reasons.append("趋势分较高：说明这个方向在当前统一数据层里表现活跃。")
        elif trend_score >= 45:
            reasons.append("趋势分中等：有一定热度，但还没到明显爆发阶段。")
        else:
            reasons.append("趋势分偏低：目前库内出现频率还不高。")

        if demand_score >= 65:
            reasons.append("需求分较高：统一市场信号显示需求侧基础较好。")
        elif demand_score >= 45:
            reasons.append("需求分中等：说明有需求，但还需要更多真实平台样本。")
        else:
            reasons.append("需求分偏弱：当前库内评论和口碑样本还不够多。")

        if competition_score >= 70:
            reasons.append("竞争分偏高：同类商品数量和评论基础都不低，新切入要更谨慎。")
        elif competition_score >= 45:
            reasons.append("竞争分中等：能做，但最好找差异化卖点。")
        else:
            reasons.append("竞争分相对可控：库内同类竞争压力暂时不算大。")

        if opportunity_score >= 65:
            reasons.append(f"机会指数较好：综合趋势、需求、竞争与数据可信度后，当前方向值得继续看。")
        elif opportunity_score >= 45:
            reasons.append("机会指数中等：可以继续观察，适合补充更多供应链和平台数据。")
        else:
            reasons.append("机会指数偏弱：现有样本太少，暂时不适合下强结论。")
        reasons.append(f"当前市场信号可信度约为 {confidence_score:.1f} / 100。")

        return reasons[:6]

    def _recommendation(self, recommendation_score: float, competition_score: float) -> str:
        if recommendation_score >= 70 and competition_score < 68:
            return "推荐关注"
        if recommendation_score >= 48:
            return "继续观察"
        return "暂不推荐"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(100.0, value))


market_intelligence_engine = MarketIntelligenceEngine()
