from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class AmazonMarketSignal(TimestampMixin, Base):
    __tablename__ = "amazon_market_signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    marketplace: Mapped[str] = mapped_column(String(50), index=True)
    bsr_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    seller_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price_min: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    price_max: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    price_average: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    competition_density: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    demand_signal: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    captured_at: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="partial")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class AmazonMarketHistory(TimestampMixin, Base):
    __tablename__ = "amazon_market_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    marketplace: Mapped[str] = mapped_column(String(50), index=True)
    bsr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviews: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    seller_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    captured_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
