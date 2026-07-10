from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business_opportunity_history import BusinessOpportunityHistory


class BusinessOpportunityHistoryRepository:
    def create(
        self,
        db: Session,
        *,
        keyword: str,
        market: str,
        market_score: float,
        supplier_score: float,
        profit_margin: float,
        opportunity_score: float,
        decision: str,
        execution_result: str | None,
        shopify_action: str | None,
        actual_result: dict | None,
        snapshot: dict,
        note: str | None = None,
    ) -> BusinessOpportunityHistory:
        record = BusinessOpportunityHistory(
            keyword=keyword,
            market=market,
            market_score=market_score,
            supplier_score=supplier_score,
            profit_margin=profit_margin,
            opportunity_score=opportunity_score,
            decision=decision,
            execution_result=execution_result,
            shopify_action=shopify_action,
            actual_result=actual_result or {},
            snapshot=snapshot,
            note=note,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def latest(self, db: Session, *, keyword: str, market: str) -> BusinessOpportunityHistory | None:
        stmt = (
            select(BusinessOpportunityHistory)
            .where(BusinessOpportunityHistory.keyword == keyword)
            .where(BusinessOpportunityHistory.market == market)
            .order_by(BusinessOpportunityHistory.created_at.desc(), BusinessOpportunityHistory.id.desc())
        )
        return db.scalar(stmt)

    def list_recent(self, db: Session, *, limit: int = 50) -> list[BusinessOpportunityHistory]:
        stmt = (
            select(BusinessOpportunityHistory)
            .order_by(BusinessOpportunityHistory.created_at.desc(), BusinessOpportunityHistory.id.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt))

    def update_actual_result(
        self,
        db: Session,
        *,
        record_id: int,
        actual_result: dict,
        execution_result: str | None = None,
        note: str | None = None,
    ) -> BusinessOpportunityHistory | None:
        record = db.get(BusinessOpportunityHistory, record_id)
        if not record:
            return None
        record.actual_result = actual_result
        if execution_result is not None:
            record.execution_result = execution_result
        if note is not None:
            record.note = note
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


business_opportunity_history_repository = BusinessOpportunityHistoryRepository()
