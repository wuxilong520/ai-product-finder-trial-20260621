from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product_intelligence import ProductIntelligence


class ProductIntelligenceRepository:
    def get_by_product_id(self, db: Session, product_id: int) -> ProductIntelligence | None:
        return db.scalar(select(ProductIntelligence).where(ProductIntelligence.product_id == product_id))

    def upsert(
        self,
        db: Session,
        *,
        product_id: int,
        market_score: float,
        competition_score: float,
        profit_score: float,
        risk_score: float,
        recommendation_score: float,
        recommendation: str,
        reasons: list[str],
    ) -> ProductIntelligence:
        existing = self.get_by_product_id(db, product_id)
        if existing:
            existing.market_score = market_score
            existing.competition_score = competition_score
            existing.profit_score = profit_score
            existing.risk_score = risk_score
            existing.recommendation_score = recommendation_score
            existing.recommendation = recommendation
            existing.reasons = reasons
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        record = ProductIntelligence(
            product_id=product_id,
            market_score=market_score,
            competition_score=competition_score,
            profit_score=profit_score,
            risk_score=risk_score,
            recommendation_score=recommendation_score,
            recommendation=recommendation,
            reasons=reasons,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


product_intelligence_repository = ProductIntelligenceRepository()
