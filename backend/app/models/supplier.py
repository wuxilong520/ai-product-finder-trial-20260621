from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    platform: Mapped[str] = mapped_column(String(50), index=True)
    supplier_type: Mapped[str] = mapped_column(String(50), nullable=False, default="trader")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    min_order_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_range: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)
    transaction_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    factory_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trust_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    certification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="cache_database")
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supplier_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    product_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    factory_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    delivery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    price_history: Mapped[list] = mapped_column(json_field, nullable=False, default=list)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unverified")
    is_authorized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_verified_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SupplierProduct(TimestampMixin, Base):
    __tablename__ = "supplier_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    product_title: Mapped[str] = mapped_column(Text, nullable=False)
    product_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    images: Mapped[list] = mapped_column(json_field, nullable=False, default=list)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="cache_database")
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    factory_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class SupplyAnalysisHistory(TimestampMixin, Base):
    __tablename__ = "supply_analysis_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_market: Mapped[str] = mapped_column(String(50), index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    supplier_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_mock: Mapped[bool] = mapped_column(nullable=False, default=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class SupplySupplierHistory(TimestampMixin, Base):
    __tablename__ = "supply_supplier_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String(255), index=True)
    platform: Mapped[str] = mapped_column(String(50), index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    product_title: Mapped[str] = mapped_column(Text, nullable=False)
    product_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="cache_database")
    price_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    min_order_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gross_profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    margin_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock_change: Mapped[str | None] = mapped_column(String(50), nullable=True)
    feedback_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class SupplierExtensionImport(TimestampMixin, Base):
    __tablename__ = "supplier_extension_imports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="1688_extension")
    product_title: Mapped[str] = mapped_column(Text, nullable=False)
    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    payload_json: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)


class SupplierPriceHistory(TimestampMixin, Base):
    __tablename__ = "supplier_price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("supplier_products.id", ondelete="SET NULL"), index=True, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    moq: Mapped[int | None] = mapped_column(Integer, nullable=True)
    record_source: Mapped[str] = mapped_column(String(50), nullable=False, default="cache_database")
