from pydantic import BaseModel, Field


class MarketAnalyzeRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="需要分析的市场关键词", examples=["air fryer"])


class MarketAnalyzeResponse(BaseModel):
    trend_score: float
    demand_score: float
    competition_score: float
    opportunity_score: float
    recommendation_score: float
    recommendation: str
    reasons: list[str]
    category: str | None = None
    source: str
    market_score: float | None = None
    competition_level: str | None = None
    market_saturation: float | None = None
    entry_barrier: str | None = None
    confidence: float | None = None
    risk_flags: list[str] = Field(default_factory=list)
    is_mock: bool | None = None
    mock_penalty: float | None = None
    reasoning: dict | None = None
    platform_signals: dict | None = None
    keyword_cluster: dict | None = None
    platform_compatibility: dict | None = None
    data_source_map: dict | None = None
