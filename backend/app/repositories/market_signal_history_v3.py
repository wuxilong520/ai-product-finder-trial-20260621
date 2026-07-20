from sqlalchemy.orm import Session

from app.models.market_signal_history_v3 import MarketSignalHistoryV3


class MarketSignalHistoryV3Repository:
    def list_recent(self, db: Session, *, keyword: str, region: str, limit: int = 12) -> list[MarketSignalHistoryV3]:
        return (
            db.query(MarketSignalHistoryV3)
            .filter(MarketSignalHistoryV3.keyword == keyword, MarketSignalHistoryV3.region == region)
            .order_by(MarketSignalHistoryV3.created_at.desc(), MarketSignalHistoryV3.id.desc())
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
        trend_direction: str,
        real_data_ratio: float,
    ) -> MarketSignalHistoryV3:
        record = MarketSignalHistoryV3(
            keyword=keyword,
            region=region,
            market_score=market_score,
            trend_direction=trend_direction,
            real_data_ratio=real_data_ratio,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


market_signal_history_v3_repository = MarketSignalHistoryV3Repository()
