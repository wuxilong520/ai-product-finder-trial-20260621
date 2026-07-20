from sqlalchemy.orm import Session

from app.models.market_analysis_history import MarketAnalysisHistory


class MarketAnalysisHistoryRepository:
    def latest_for_keyword(
        self,
        db: Session,
        *,
        keyword: str,
        region: str,
        workspace_id: int | None = None,
    ) -> MarketAnalysisHistory | None:
        return (
            db.query(MarketAnalysisHistory)
            .filter(
                MarketAnalysisHistory.keyword == keyword,
                MarketAnalysisHistory.region == region,
            )
            .filter(MarketAnalysisHistory.workspace_id == workspace_id if workspace_id is not None else True)
            .order_by(MarketAnalysisHistory.created_at.desc(), MarketAnalysisHistory.id.desc())
            .first()
        )

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
        previous_score: float | None,
        current_score: float | None,
        change_rate: float | None,
        trend_direction: str | None,
        snapshot: dict,
        workspace_id: int | None = None,
    ) -> MarketAnalysisHistory:
        record = MarketAnalysisHistory(
            keyword=keyword,
            region=region,
            workspace_id=workspace_id,
            category=category,
            score=score,
            trend=trend,
            competition=competition,
            source=source,
            confidence=confidence,
            is_mock=is_mock,
            previous_score=previous_score,
            current_score=current_score,
            change_rate=change_rate,
            trend_direction=trend_direction,
            snapshot=snapshot,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


market_analysis_history_repository = MarketAnalysisHistoryRepository()
