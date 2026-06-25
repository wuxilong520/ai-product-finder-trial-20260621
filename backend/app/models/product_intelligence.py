from sqlalchemy import ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class ProductIntelligence(TimestampMixin, Base):
    __tablename__ = "product_intelligence"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), unique=True, index=True)
    market_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    competition_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    profit_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(20), nullable=False)
    reasons: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)

    product = relationship("Product", back_populates="intelligence_record")
