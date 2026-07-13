from sqlalchemy.orm import Session

from app.models.commercial_signal_history import CommercialSignalHistory


class CommercialSignalHistoryRepository:
    def latest(
        self,
        db: Session,
        *,
        keyword: str,
        region: str,
        source: str,
    ) -> CommercialSignalHistory | None:
        return (
            db.query(CommercialSignalHistory)
            .filter(
                CommercialSignalHistory.keyword == keyword,
                CommercialSignalHistory.region == region,
                CommercialSignalHistory.source == source,
            )
            .order_by(CommercialSignalHistory.created_at.desc(), CommercialSignalHistory.id.desc())
            .first()
        )

    def create(
        self,
        db: Session,
        *,
        keyword: str,
        region: str,
        source: str,
        signal_score: float,
        status: str,
        reliability: float,
    ) -> CommercialSignalHistory:
        record = CommercialSignalHistory(
            keyword=keyword,
            region=region,
            source=source,
            signal_score=signal_score,
            status=status,
            reliability=reliability,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


commercial_signal_history_repository = CommercialSignalHistoryRepository()

