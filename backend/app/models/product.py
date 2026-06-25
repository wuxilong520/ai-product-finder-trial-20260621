from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id", ondelete="RESTRICT"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    external_product_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_url: Mapped[str] = mapped_column(Text, unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    title_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    current_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    original_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    platform = relationship("Platform", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    crawl_runs = relationship("CrawlRun", back_populates="product")
    analysis_results = relationship("AIAnalysisResult", back_populates="product", cascade="all, delete-orphan")
    keywords = relationship("ProductKeyword", back_populates="product", cascade="all, delete-orphan")
    sourcing_links = relationship("SourcingLink", back_populates="product", cascade="all, delete-orphan")
    intelligence_record = relationship("ProductIntelligence", back_populates="product", cascade="all, delete-orphan", uselist=False)


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    image_url: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="images")


class ProductKeyword(Base):
    __tablename__ = "product_keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    analysis_id: Mapped[int | None] = mapped_column(ForeignKey("ai_analysis_results.id", ondelete="CASCADE"), nullable=True)
    keyword_type: Mapped[str] = mapped_column(String(30))
    keyword_text: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="keywords")
    analysis = relationship("AIAnalysisResult", back_populates="keywords")


class SourcingLink(Base):
    __tablename__ = "sourcing_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    analysis_id: Mapped[int | None] = mapped_column(ForeignKey("ai_analysis_results.id", ondelete="SET NULL"), nullable=True)
    source_platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id", ondelete="RESTRICT"))
    keyword_text: Mapped[str] = mapped_column(String(255))
    search_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="sourcing_links")
    analysis = relationship("AIAnalysisResult", back_populates="sourcing_links")
