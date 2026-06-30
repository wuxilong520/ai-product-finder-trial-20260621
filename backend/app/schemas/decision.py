from pydantic import BaseModel, Field


class DecisionRecommendRequest(BaseModel):
    product_id: int = Field(..., ge=1, description="商品 ID", examples=[1])


class DecisionRecommendResponse(BaseModel):
    source_id: str | None = None
    source_type: str | None = None
    lineage_chain: list[str] = []
    truth_level: str | None = None
    confidence_score: float | None = None
    freshness_score: float | None = None
    intelligence_score: float
    market_score: float
    supplier_score: float
    profit_score: float
    risk_score: float
    market_fit_score: float | None = None
    supplier_fit_score: float | None = None
    final_score: float
    recommendation: str
    recommendation_level: str
    reasons: list[str]
