from pydantic import BaseModel, Field


class P5PredictionRequest(BaseModel):
    product_id: int = Field(..., ge=1)
    horizon_days: int = Field(default=30, ge=7, le=30)


class P5PredictionResponse(BaseModel):
    product_id: int
    keyword: str
    forecast_window_days: int
    growth_forecast: float
    demand_forecast: float
    competition_forecast: float
    profit_forecast: float
    explosion_probability: float
    reasons: list[str]


class P5RecommendationItem(BaseModel):
    product_id: int
    title: str
    title_zh: str | None
    keyword: str
    category: str | None
    recommendation_score: float
    estimated_profit: float
    recommendation: str
    truth_level: str | None = None
    source_type: str | None = None
    freshness_score: float | None = None
    reasons: list[str]


class P5RecommendationsResponse(BaseModel):
    keyword: str | None = None
    category: str | None = None
    truth_level: str | None = None
    source_type: str | None = None
    freshness_min: float | None = None
    total_scanned: int
    items: list[P5RecommendationItem]


class P5RankingEntry(BaseModel):
    product_id: int
    title: str
    score: float
    category: str | None


class P5RankingsGroup(BaseModel):
    top_10: list[P5RankingEntry]
    top_50: list[P5RankingEntry]
    top_100: list[P5RankingEntry]


class P5RankingsResponse(BaseModel):
    scanned_products: int
    profit_ranking: P5RankingsGroup
    growth_ranking: P5RankingsGroup
    risk_ranking: P5RankingsGroup
