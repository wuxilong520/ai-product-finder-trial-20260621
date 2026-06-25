from sqlalchemy import ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class SupplierMatch(TimestampMixin, Base):
    __tablename__ = "supplier_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_title: Mapped[str] = mapped_column(Text, nullable=False)
    supplier_url: Mapped[str] = mapped_column(Text, nullable=False)
    supplier_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    match_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    availability: Mapped[str] = mapped_column(String(50), nullable=False)
