from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market_intelligence import MarketIntelligence


class MarketIntelligenceRepository:
    def get_latest_by_keyword(self, db: Session, keyword: str) -> MarketIntelligence | None:
        stmt = (
            select(MarketIntelligence)
            .where(MarketIntelligence.keyword == keyword)
            .order_by(MarketIntelligence.updated_at.desc(), MarketIntelligence.id.desc())
        )
        return db.scalar(stmt)

    def create(
        self,
        db: Session,
        *,
        keyword: str,
        category: str | None,
        trend_score: float,
        demand_score: float,
        competition_score: float,
        opportunity_score: float,
        recommendation_score: float,
        recommendation: str,
        reasons: list[str],
        source: str,
    ) -> MarketIntelligence:
        record = MarketIntelligence(
            keyword=keyword,
            category=category,
            trend_score=trend_score,
            demand_score=demand_score,
            competition_score=competition_score,
            opportunity_score=opportunity_score,
            recommendation_score=recommendation_score,
            recommendation=recommendation,
            reasons=reasons,
            source=source,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


market_intelligence_repository = MarketIntelligenceRepository()
