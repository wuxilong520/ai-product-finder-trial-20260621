from sqlalchemy import String, Text, JSON, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class MarketIntelligence(TimestampMixin, Base):
    __tablename__ = "market_intelligence"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trend_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    demand_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    competition_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    opportunity_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(20), nullable=False)
    reasons: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="internal_product_library")
