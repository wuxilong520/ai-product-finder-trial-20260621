from sqlalchemy.orm import Session

from app.models.market_reality_history import MarketRealityHistory


class MarketRealityHistoryRepository:
    def latest(self, db: Session, *, keyword: str, region: str) -> MarketRealityHistory | None:
        return (
            db.query(MarketRealityHistory)
            .filter(MarketRealityHistory.keyword == keyword, MarketRealityHistory.region == region)
            .order_by(MarketRealityHistory.created_at.desc(), MarketRealityHistory.id.desc())
            .first()
        )

    def list_recent(self, db: Session, *, keyword: str, region: str, limit: int = 12) -> list[MarketRealityHistory]:
        return (
            db.query(MarketRealityHistory)
            .filter(MarketRealityHistory.keyword == keyword, MarketRealityHistory.region == region)
            .order_by(MarketRealityHistory.created_at.desc(), MarketRealityHistory.id.desc())
            .limit(limit)
            .all()
        )

    def create(
        self,
        db: Session,
        *,
        keyword: str,
        region: str,
        market_score: float,
        confidence_score: float,
        consumer_interest: float,
        commercial_intent: float,
        competition_pressure: float,
        trend_stage: str,
        sources: list[dict],
    ) -> MarketRealityHistory:
        record = MarketRealityHistory(
            keyword=keyword,
            region=region,
            market_score=market_score,
            confidence_score=confidence_score,
            consumer_interest=consumer_interest,
            commercial_intent=commercial_intent,
            competition_pressure=competition_pressure,
            trend_stage=trend_stage,
            sources=sources,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


market_reality_history_repository = MarketRealityHistoryRepository()
