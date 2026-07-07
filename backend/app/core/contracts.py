from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TrendPoint(BaseModel):
    date: str
    score: int = Field(..., ge=0, le=100)


class MarketInsight(BaseModel):
    source: str
    keyword: str
    market: str
    trend_direction: str
    demand_score: int = Field(..., ge=0, le=100)
    competition_score: int = Field(..., ge=0, le=100)
    trend_points: list[TrendPoint]
    summary: str
    market_score: float = 0
    recommendation: str = ""
    confidence: float = 0
    risk_flags: list[str] = Field(default_factory=list)
    platform_signals: dict = Field(default_factory=dict)
    keyword_cluster: dict = Field(default_factory=dict)
    platform_compatibility: dict = Field(default_factory=dict)
    is_mock: bool = False
    mock_penalty_applied: bool = False


class SupplyOffer(BaseModel):
    source: str
    supplier_id: str
    supplier_name: str
    keyword: str
    product_title: str
    price: float
    min_order_qty: int
    rating: float
    shipping_days: int
    currency: str = "CNY"


class ProfitBreakdown(BaseModel):
    currency: str = "CNY"
    cost_price: float
    selling_price: float
    estimated_sell_price: float
    supply_cost: float
    shipping_cost: float
    platform_fee: float
    ad_cost: float
    profit: float
    margin: float
    break_even_price: float
    estimated_profit: float
    estimated_margin_rate: float
    cost_estimate: float = 0
    profit_margin: float = 0
    shopify_reference_price: float = 0
    alibaba_reference_cost: float = 0
    profit_truth_score: float = 0


class DataTrustReport(BaseModel):
    data: Any
    source_type: str
    freshness_score: float = Field(..., ge=0, le=1)
    confidence_score: float = Field(..., ge=0, le=1)
    trust_level: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    is_mock: bool = False
    is_expired: bool = False
    fallback_marked: bool = False


class StrategyPlan(BaseModel):
    strategy_mode: str
    objective: str
    action_plan: list[str] = Field(default_factory=list)
    execution_steps: list[str] = Field(default_factory=list)
    listing_recommendation: str = ""
    supply_validation: list[str] = Field(default_factory=list)
    business_constraints: dict = Field(default_factory=dict)


class AnalysisOutcome(BaseModel):
    score: int = Field(..., ge=0, le=100)
    recommend: bool
    risk: str
    profit_estimate: float
    reasoning: str
    action: str
    trace: list[str] = Field(default_factory=list)
    trust_adjusted_score: float = 0
    fallback_marked: bool = False


class DecisionRecord(BaseModel):
    keyword: str
    market: str
    verdict: str
    confidence_score: int = Field(..., ge=0, le=100)
    recommended_price: float
    risk_level: str
    reasons: list[str]
    decision_score: float = 0
    strategy_mode: str = "sourcing"
    trust_adjusted_score: float = 0
    real_profit_estimate: float = 0
    action_plan: list[str] = Field(default_factory=list)
    execution_steps: list[str] = Field(default_factory=list)
    feedback_keys: list[str] = Field(default_factory=list)
    trusted_market_data: dict = Field(default_factory=dict)
    supply_validation: list[str] = Field(default_factory=list)
    listing_recommendation: str = ""
    business_constraints: dict = Field(default_factory=dict)
    data_trust: dict = Field(default_factory=dict)
    action_level: str = "WATCH"
    execution_allowed: bool = False
    execution_block_reason: str = ""
    safety_gate_result: dict = Field(default_factory=dict)
    final_listing_permission: bool = False
    override_history: list[dict] = Field(default_factory=list)
    platform_execution_status: str = "blocked"
    execution_bridge_mapping: dict = Field(default_factory=dict)
    execution_queue_status: str = "idle"
    feedback_signal: dict = Field(default_factory=dict)
    ai_adjustment_suggestion: dict = Field(default_factory=dict)
    commercial_ready: bool = False
    product_mode: str = "demo_mode"
    launch_blockers: list[str] = Field(default_factory=list)
    scale_recommendation: str = ""


class TraceNode(BaseModel):
    step: str
    adapter: str | None = None
    status: str
    message: str
    payload: dict = Field(default_factory=dict)


class ExplainPacket(BaseModel):
    summary: str
    reasons: list[str]
    risk_notes: list[str]
    next_actions: list[str]


class ListingDraft(BaseModel):
    channel: str
    product_title: str
    seo_title: str
    listing_title: str
    listing_description: str
    description: str
    keywords: list[str]
    bullet_points: list[str]
    image_structure: list[str]
    selling_points: list[str]
    tags: list[str]
    price_suggestion: float
    suggested_price: float


class OAuthSession(BaseModel):
    channel: str
    shop_domain: str
    authorize_url: str
    state: str
    connected: bool
    access_token: str | None = None


class PublishReceipt(BaseModel):
    channel: str
    status: str
    listing_id: str
    publish_url: str
    message: str


class AnalyzeBundle(BaseModel):
    market_insight: MarketInsight
    supply_offers: list[SupplyOffer]
    selected_offer: SupplyOffer
    profit_breakdown: ProfitBreakdown
    analysis_outcome: AnalysisOutcome
    trust_report: dict = Field(default_factory=dict)
    trace: list[TraceNode]
    explain: ExplainPacket
