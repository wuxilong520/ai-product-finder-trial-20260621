from sqlalchemy import ForeignKey, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class BusinessTruthDecision(TimestampMixin, Base):
    __tablename__ = "business_truth_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, unique=True)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    real_market_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    market_price_min: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    market_price_max: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    demand_signal: Mapped[str] = mapped_column(String(30), nullable=False)
    supplier_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    shipping_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    platform_fee: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    packaging_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    profit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    profit_margin: Mapped[float] = mapped_column(Numeric(7, 4), nullable=False)
    break_even_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    phase4_final_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    truth_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    truth_recommendation: Mapped[str] = mapped_column(String(40), nullable=False)
    truth_level: Mapped[str] = mapped_column(String(2), nullable=False)
    still_uses_simulated_data: Mapped[bool] = mapped_column(nullable=False, default=True)
    simulated_dependencies: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
    cost_breakdown: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)
    external_market_snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)
    reasons: Mapped[list[str]] = mapped_column(json_field, nullable=False, default=list)
