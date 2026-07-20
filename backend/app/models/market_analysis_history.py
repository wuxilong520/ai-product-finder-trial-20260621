from sqlalchemy import JSON, Boolean, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


json_field = JSON().with_variant(JSONB, "postgresql")


class MarketAnalysisHistory(TimestampMixin, Base):
    __tablename__ = "market_analysis_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    region: Mapped[str] = mapped_column(String(50), index=True)
    workspace_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    trend: Mapped[float] = mapped_column(Float, nullable=False)
    competition: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    is_mock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    previous_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    change_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    trend_direction: Mapped[str | None] = mapped_column(String(50), nullable=True)
    snapshot: Mapped[dict] = mapped_column(json_field, nullable=False, default=dict)
