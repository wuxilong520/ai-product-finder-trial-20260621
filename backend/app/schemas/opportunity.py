from pydantic import BaseModel, Field


class OpportunityAnalyzeRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    marketplace: str = Field(default="US")
    region: str = Field(default="US")


class OpportunityAnalyzeResponse(BaseModel):
    keyword: str
    marketplace: str
    region: str
    market_score: float
    amazon_score: float
    supplier_score: float
    profit_margin: float
    opportunity_score: float
    recommendation: str
    confidence: float
    risk_flags: list[str] = Field(default_factory=list)
    market_status: str | None = None
    amazon_status: str | None = None
    supply_status: str | None = None
    profit_status: str | None = None
    amazon_signal: dict | None = None
    selected_supplier: dict | None = None
    real_profit: dict | None = None
    decision: dict | None = None
