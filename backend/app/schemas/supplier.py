from pydantic import BaseModel, Field


class SupplierMatchRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="供应链匹配关键词", examples=["air fryer"])
    category: str | None = None
    target_market: str = "global"
    expected_price: float | None = None
    quantity: int = 100


class SupplierMatchItem(BaseModel):
    product_id: int | None = None
    supplier_name: str | None = None
    platform: str
    supplier_title: str
    supplier_url: str
    supplier_price: float | None = None
    currency: str | None = None
    match_score: float
    availability: str
    moq: int | None = None
    supplier_score: float | None = None
    supplier_real_score: float | None = None
    supplier_level: str | None = None
    supplier_confidence: float | None = None
    price_competitiveness_score: float | None = None
    moq_score: float | None = None
    profit_estimate: float | None = None
    risk_flags: list[str] = Field(default_factory=list)
    data_source: str | None = None
    source_type: str | None = None
    risk_level: str | None = None
    supplier_type: str | None = None
    location: str | None = None
    certification: str | None = None
    delivery_time: int | None = None
    price_change: float | None = None
    stock_change: str | None = None
    procurement_recommendation: str | None = None


class SupplierMatchResponse(BaseModel):
    suppliers: list[SupplierMatchItem]
    supplier_score: float | None = None
    supplier_real_score: float | None = None
    supplier_confidence: float | None = None
    confidence: float | None = None
    source_type: str | None = None
    risk_level: str | None = None
    risk_flags: list[str] = Field(default_factory=list)
    cost_estimate: dict | None = None
    profit_preview: dict | None = None
    procurement_recommendation: dict | None = None
    is_mock: bool | None = None


class SupplierIntelligenceResponse(BaseModel):
    supplier: dict
    real_score: float
    authenticity_score: float
    risk: dict
    price_score: float
    moq_score: float
    stability_score: float
    supplier_confidence: float
    recommendation: str
