from sqlalchemy import JSON, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class BusinessOpportunityHistory(TimestampMixin, Base):
    __tablename__ = "business_opportunity_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    market: Mapped[str] = mapped_column(String(50), index=True)
    market_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supplier_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    profit_margin: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    opportunity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    decision: Mapped[str] = mapped_column(String(20), nullable=False, default="WATCH")
    execution_result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shopify_action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    actual_result: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)
    snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
