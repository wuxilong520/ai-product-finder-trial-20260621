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
