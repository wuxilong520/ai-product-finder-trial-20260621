from pydantic import BaseModel, Field


class DecisionRecommendRequest(BaseModel):
    product_id: int = Field(..., ge=1, description="商品 ID", examples=[1])


class DecisionRecommendResponse(BaseModel):
    intelligence_score: float
    market_score: float
    supplier_score: float
    profit_score: float
    risk_score: float
    final_score: float
    recommendation: str
    recommendation_level: str
    reasons: list[str]
