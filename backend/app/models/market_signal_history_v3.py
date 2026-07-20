from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class MarketSignalHistoryV3(TimestampMixin, Base):
    __tablename__ = "market_signal_history_v3"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    region: Mapped[str] = mapped_column(String(50), index=True)
    market_score: Mapped[float] = mapped_column(Float, nullable=False)
    trend_direction: Mapped[str] = mapped_column(String(50), nullable=False, default="flat")
    real_data_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
