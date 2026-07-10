from pydantic import BaseModel, Field


class OpportunityAnalyzeRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    marketplace: str = Field(default="US")
    region: str = Field(default="US")


class OpportunityAnalyzeResponse(BaseModel):
    keyword: str
    market: str
    market_signal: dict
    amazon_signal: dict
    supplier_signal: dict
    profit_signal: dict
    decision: str
    execution: dict
    market_score: float
    supplier_score: float
    profit_margin: float
    opportunity_score: float
    confidence: float
    risk_flags: list[str] = Field(default_factory=list)
    source_status: dict = Field(default_factory=dict)
    shopify_action: str = "blocked"
    shopify_draft: dict = Field(default_factory=dict)
    feedback_signal: dict = Field(default_factory=dict)
    history_id: int | None = None


class OpportunityExecuteRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    marketplace: str = Field(default="US")
    region: str = Field(default="US")
    shop_domain: str = Field(..., min_length=1)


class OpportunityExecuteResponse(BaseModel):
    keyword: str
    market: str
    recommendation: str
    shopify_action: str
    execution: dict = Field(default_factory=dict)
    draft: dict = Field(default_factory=dict)
    feedback: dict = Field(default_factory=dict)
    history_id: int | None = None


class OpportunityHistoryItem(BaseModel):
    id: int
    keyword: str
    market: str
    market_score: float
    supplier_score: float
    profit_margin: float
    opportunity_score: float
    decision: str
    execution_result: str | None = None
    shopify_action: str | None = None
    actual_result: dict = Field(default_factory=dict)
    created_at: str = ""


class OpportunityHistoryResponse(BaseModel):
    items: list[OpportunityHistoryItem] = Field(default_factory=list)
