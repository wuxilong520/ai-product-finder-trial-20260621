from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class MarketSignalHistory(TimestampMixin, Base):
    __tablename__ = "market_signal_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    region: Mapped[str] = mapped_column(String(50), index=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    trend: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    signal_strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    change_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
