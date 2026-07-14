from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class ProductGroup(TimestampMixin, Base):
    __tablename__ = "product_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    canonical_keyword: Mapped[str] = mapped_column(String(255), index=True)
    canonical_title: Mapped[str] = mapped_column(Text, nullable=False)
    representative_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    similarity_snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class ProcurementPoolItem(TimestampMixin, Base):
    __tablename__ = "procurement_pool_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    product_group_id: Mapped[int | None] = mapped_column(ForeignKey("product_groups.id", ondelete="SET NULL"), index=True, nullable=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False, default="1688")
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplier_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_profit: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    market_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NEW", index=True)
    metadata_json: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class ProcurementSupplierItem(TimestampMixin, Base):
    __tablename__ = "procurement_supplier_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    pool_item_id: Mapped[int] = mapped_column(ForeignKey("procurement_pool_items.id", ondelete="CASCADE"), index=True, nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"), index=True, nullable=True)
    supplier_product_id: Mapped[int | None] = mapped_column(ForeignKey("supplier_products.id", ondelete="SET NULL"), index=True, nullable=True)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    moq: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delivery_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    supplier_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supplier_truth_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="LOCAL_DATABASE")
    metadata_json: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class SupplierRealityHistory(TimestampMixin, Base):
    __tablename__ = "supplier_reality_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"), index=True, nullable=True)
    pool_item_id: Mapped[int | None] = mapped_column(ForeignKey("procurement_pool_items.id", ondelete="CASCADE"), index=True, nullable=True)
    truth_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    price_truth_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stability_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class ProcurementAnalysisHistory(TimestampMixin, Base):
    __tablename__ = "procurement_analysis_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    pool_item_id: Mapped[int] = mapped_column(ForeignKey("procurement_pool_items.id", ondelete="CASCADE"), index=True, nullable=False)
    product_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    market_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supplier_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    profit_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    recommendation: Mapped[str] = mapped_column(String(40), nullable=False, default="谨慎观察")
    reason: Mapped[list] = mapped_column(json_field, nullable=False, default=list)
    snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)
