from sqlalchemy.orm import Session

from app.models.market_analysis_history import MarketAnalysisHistory


class MarketAnalysisHistoryRepository:
    def create(
        self,
        db: Session,
        *,
        keyword: str,
        region: str,
        category: str | None,
        score: float,
        trend: float,
        competition: float,
        source: str,
        confidence: float,
        is_mock: bool,
        snapshot: dict,
    ) -> MarketAnalysisHistory:
        record = MarketAnalysisHistory(
            keyword=keyword,
            region=region,
            category=category,
            score=score,
            trend=trend,
            competition=competition,
            source=source,
            confidence=confidence,
            is_mock=is_mock,
            snapshot=snapshot,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


market_analysis_history_repository = MarketAnalysisHistoryRepository()
