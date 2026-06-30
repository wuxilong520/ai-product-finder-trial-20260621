from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business_truth import BusinessTruthDecision


class BusinessTruthDecisionRepository:
    def get_by_product_id(self, db: Session, product_id: int, workspace_id: int | None = None) -> BusinessTruthDecision | None:
        stmt = (
            select(BusinessTruthDecision)
            .where(BusinessTruthDecision.product_id == product_id)
            .order_by(BusinessTruthDecision.updated_at.desc(), BusinessTruthDecision.id.desc())
        )
        if workspace_id is not None:
            stmt = stmt.where(BusinessTruthDecision.workspace_id == workspace_id)
        return db.scalar(stmt)

    def get_by_task_id(self, db: Session, task_id: int, workspace_id: int | None = None) -> BusinessTruthDecision | None:
        stmt = (
            select(BusinessTruthDecision)
            .where(BusinessTruthDecision.task_id == task_id)
            .order_by(BusinessTruthDecision.updated_at.desc(), BusinessTruthDecision.id.desc())
        )
        if workspace_id is not None:
            stmt = stmt.where(BusinessTruthDecision.workspace_id == workspace_id)
        return db.scalar(stmt)

    def upsert(self, db: Session, *, product_id: int, task_id: int | None = None, **payload) -> BusinessTruthDecision:
        existing = self.get_by_task_id(db, task_id) if task_id is not None else self.get_by_product_id(db, product_id)
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            existing.product_id = product_id
            existing.task_id = task_id
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        record = BusinessTruthDecision(product_id=product_id, task_id=task_id, **payload)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


business_truth_decision_repository = BusinessTruthDecisionRepository()
