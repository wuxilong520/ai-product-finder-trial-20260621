from __future__ import annotations

from pydantic import BaseModel, Field


class MarketSignalBlock(BaseModel):
    demand_score: float = 0.0
    trend_direction: str = "flat"
    competition_level: str = "medium"
    confidence: float = 0.0


class AmazonSignalBlock(BaseModel):
    demand_score: float = 0.0
    review_density: float = 0.0
    competition_density: float = 0.0
    price_range: dict = Field(default_factory=dict)


class SupplierSignalBlock(BaseModel):
    supplier_score: float = 0.0
    supplier_source: str = "unavailable"
    product_cost: float = 0.0
    MOQ: int = 0
    supplier_confidence: float = 0.0


class ProfitSignalBlock(BaseModel):
    cost: float = 0.0
    shipping_cost: float = 0.0
    platform_fee: float = 0.0
    ad_cost: float = 0.0
    expected_price: float = 0.0
    gross_margin: float = 0.0
    net_margin: float = 0.0
    profit_confidence: float = 0.0


class ExecutionSignalBlock(BaseModel):
    shopify_ready: bool = False
    draft_allowed: bool = False
    publish_allowed: bool = False


class BusinessOpportunityV3(BaseModel):
    keyword: str
    market: str
    market_signal: MarketSignalBlock
    amazon_signal: AmazonSignalBlock
    supplier_signal: SupplierSignalBlock
    profit_signal: ProfitSignalBlock
    decision: str
    execution: ExecutionSignalBlock
    market_score: float = 0.0
    supplier_score: float = 0.0
    profit_margin: float = 0.0
    opportunity_score: float = 0.0
    confidence: float = 0.0
    risk_flags: list[str] = Field(default_factory=list)
    source_status: dict = Field(default_factory=dict)
    shopify_action: str = "blocked"
    shopify_draft: dict = Field(default_factory=dict)
    feedback_signal: dict = Field(default_factory=dict)
    history_id: int | None = None
