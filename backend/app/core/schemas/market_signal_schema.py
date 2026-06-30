from __future__ import annotations

from app.core.schemas.common import BaseDataSchema


class MarketSignalSchema(BaseDataSchema):
    id: str
    keyword: str
    category: str | None = None
    trend_score: float
    growth_rate: float
    competition_index: float
    demand_level: float
    source_platform: str
    confidence_score: float
