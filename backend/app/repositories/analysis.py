from sqlalchemy.orm import Session

from app.models.analysis import AIAnalysisResult


class AnalysisRepository:
    def create(self, db: Session, **kwargs) -> AIAnalysisResult:
        record = AIAnalysisResult(**kwargs)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def latest_by_product_id(self, db: Session, product_id: int) -> AIAnalysisResult | None:
        from sqlalchemy import desc, select

        return db.scalar(
            select(AIAnalysisResult)
            .where(AIAnalysisResult.product_id == product_id)
            .order_by(desc(AIAnalysisResult.id))
        )


analysis_repository = AnalysisRepository()
