from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business_truth import BusinessTruthDecision


class BusinessTruthDecisionRepository:
    def get_by_product_id(self, db: Session, product_id: int) -> BusinessTruthDecision | None:
        stmt = select(BusinessTruthDecision).where(BusinessTruthDecision.product_id == product_id)
        return db.scalar(stmt)

    def upsert(self, db: Session, *, product_id: int, **payload) -> BusinessTruthDecision:
        existing = self.get_by_product_id(db, product_id)
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        record = BusinessTruthDecision(product_id=product_id, **payload)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


business_truth_decision_repository = BusinessTruthDecisionRepository()
