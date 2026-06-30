from __future__ import annotations

from app.core.schemas.common import BaseDataSchema


class DecisionResultSchema(BaseDataSchema):
    product_id: int
    decision: str
    profit_range: dict
    risk_level: str
    reasoning: list[str]
    market_fit_score: float
    supplier_fit_score: float
    profit_score: float
    risk_score: float
    reliability_score: float
    final_score: float
