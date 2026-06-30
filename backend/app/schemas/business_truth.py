from pydantic import BaseModel, Field


class BusinessTruthRecommendRequest(BaseModel):
    product_id: int = Field(..., ge=1, description="商品 ID", examples=[1])


class BusinessTruthRecommendResponse(BaseModel):
    keyword: str
    selling_price: float
    real_market_price: float
    market_price_min: float
    market_price_max: float
    demand_signal: str
    supplier_cost: float
    shipping_cost: float
    platform_fee: float
    packaging_cost: float
    exchange_rate: float
    total_cost: float
    profit: float
    profit_margin: float
    break_even_price: float
    phase4_final_score: float
    truth_score: float
    truth_recommendation: str
    truth_level: str
    source_id: str | None = None
    lineage_chain: list[str] = []
    confidence_score: float | None = None
    freshness_score: float | None = None
    still_uses_simulated_data: bool
    simulated_dependencies: list[str]
    cost_breakdown: dict
    external_market_snapshot: dict
    reasons: list[str]
