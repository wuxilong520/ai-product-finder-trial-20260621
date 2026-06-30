from sqlalchemy import ForeignKey, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class DecisionRecommendation(TimestampMixin, Base):
    __tablename__ = "decision_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    task_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    workspace_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    api_key_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lineage_chain: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
    truth_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    freshness_score: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    intelligence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    market_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    supplier_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    profit_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    market_fit_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    supplier_fit_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    final_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(30), nullable=False)
    recommendation_level: Mapped[str] = mapped_column(String(2), nullable=False)
    reasons: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
    result_json: Mapped[dict | None] = mapped_column(json_field, nullable=True)
