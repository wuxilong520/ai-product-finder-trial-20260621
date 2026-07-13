from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class MarketRealityHistory(TimestampMixin, Base):
    __tablename__ = "market_reality_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    region: Mapped[str] = mapped_column(String(50), index=True)
    market_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    consumer_interest: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    commercial_intent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    competition_pressure: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trend_stage: Mapped[str] = mapped_column(String(30), nullable=False, default="stable")
    sources: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
