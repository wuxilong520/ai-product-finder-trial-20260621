from pydantic import BaseModel, Field


class MarketAnalyzeRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="需要分析的市场关键词", examples=["air fryer"])
    region: str = Field(default="global", description="市场区域，例如 global / US / UK / EU")
    category: str | None = Field(default=None, description="可选类目")


class MarketConnectRequest(BaseModel):
    shop_domain: str = Field(..., min_length=3, description="Shopify 店铺域名，例如 your-store.myshopify.com")


class MarketAnalyzeResponse(BaseModel):
    keyword: str | None = None
    region: str | None = None
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
    data_sources: dict | None = None
    market_signals: list[dict] = Field(default_factory=list)
    market_growth: float | None = None
    market_opportunity: dict | None = None
    source_status: dict | None = None
    trend_direction: str | None = None
    trend_strength: float | None = None
    competition: float | None = None
    risk_level: str | None = None
    real_ratio: float | None = None
    partial_ratio: float | None = None
    mock_ratio: float | None = None
    missing_credentials: list[str] = Field(default_factory=list)
    real_data_ratio: float | None = None
    confidence_score: float | None = None
    source_reliability: dict | None = None
    evidence_sources: list[dict] = Field(default_factory=list)
    profit_potential: float | None = None
    commercial_score: float | None = None
    commercial_reality_score: float | None = None
    real_sales_signal: float | None = None
    customer_validation: float | None = None
    market_fit_score: float | None = None
    repeat_purchase_signal: float | None = None
    profit_validation: float | None = None
    consumer_interest: float | None = None
    consumer_interest_score: float | None = None
    commercial_intent: float | None = None
    commercial_intent_score: float | None = None
    commercial_competition: float | None = None
    ad_market_value: float | None = None
    brand_activity: float | None = None
    purchase_signal: float | None = None
    competition_pressure: float | None = None
    trend_stage: str | None = None
    trend_lifecycle: str | None = None
    reality_sources: list[dict] = Field(default_factory=list)
    opportunity_reason: str | None = None
