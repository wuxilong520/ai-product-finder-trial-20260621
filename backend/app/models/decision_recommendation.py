from sqlalchemy import ForeignKey, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class DecisionRecommendation(TimestampMixin, Base):
    __tablename__ = "decision_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, unique=True)
    intelligence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    market_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    supplier_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    profit_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    final_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(30), nullable=False)
    recommendation_level: Mapped[str] = mapped_column(String(2), nullable=False)
    reasons: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
