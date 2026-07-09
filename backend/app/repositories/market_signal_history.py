from sqlalchemy.orm import Session

from app.models.market_signal_history import MarketSignalHistory


class MarketSignalHistoryRepository:
    def latest(
        self,
        db: Session,
        *,
        keyword: str,
        region: str,
        source: str,
    ) -> MarketSignalHistory | None:
        return (
            db.query(MarketSignalHistory)
            .filter(
                MarketSignalHistory.keyword == keyword,
                MarketSignalHistory.region == region,
                MarketSignalHistory.source == source,
            )
            .order_by(MarketSignalHistory.created_at.desc(), MarketSignalHistory.id.desc())
            .first()
        )

    def create(
        self,
        db: Session,
        *,
        keyword: str,
        region: str,
        source: str,
        score: float,
        trend: float,
        status: str,
    ) -> MarketSignalHistory:
        record = MarketSignalHistory(
            keyword=keyword,
            region=region,
            source=source,
            score=score,
            trend=trend,
            status=status,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


market_signal_history_repository = MarketSignalHistoryRepository()
