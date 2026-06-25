from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.decision_recommendation import DecisionRecommendation


class DecisionRecommendationRepository:
    def get_by_product_id(self, db: Session, product_id: int) -> DecisionRecommendation | None:
        return db.scalar(select(DecisionRecommendation).where(DecisionRecommendation.product_id == product_id))

    def upsert(self, db: Session, *, product_id: int, **payload) -> DecisionRecommendation:
        existing = self.get_by_product_id(db, product_id)
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        record = DecisionRecommendation(product_id=product_id, **payload)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


decision_recommendation_repository = DecisionRecommendationRepository()
