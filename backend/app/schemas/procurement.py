from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.supply_extension import SupplyImportPayload


class ProcurementPoolSupplierItem(BaseModel):
    id: int
    supplier_id: int | None = None
    supplier_name: str
    price: float
    moq: int | None = None
    delivery_time: int | None = None
    supplier_score: float
    risk_score: float
    supplier_truth_score: float
    source_type: str


class ProcurementAnalysisPayload(BaseModel):
    product_score: float
    market_score: float
    supplier_score: float
    profit_score: float
    risk_level: str
    recommendation: str
    reason: list[str] = Field(default_factory=list)
    profit: dict = Field(default_factory=dict)
    market: dict = Field(default_factory=dict)


class ProcurementPoolItemResponse(BaseModel):
    id: int
    keyword: str
    category: str | None = None
    title: str
    image: str | None = None
    description: str | None = None
    source_platform: str
    source_url: str | None = None
    supplier_count: int
    min_price: float
    max_price: float
    avg_price: float
    estimated_profit: float
    market_score: float
    status: str
    supplier_score: float
    risk_level: str
    created_at: str
    suppliers: list[ProcurementPoolSupplierItem] = Field(default_factory=list)
    analysis: ProcurementAnalysisPayload | None = None


class ProcurementPoolListResponse(BaseModel):
    items: list[ProcurementPoolItemResponse]
    total: int


class ProcurementFavoriteRequest(BaseModel):
    pool_item_id: int
    action: str = Field(..., min_length=1, max_length=32)


class ProcurementFavoriteResponse(BaseModel):
    ok: bool
    status: str
    pool_item_id: int


class ProcurementCompareResponse(BaseModel):
    items: list[ProcurementPoolItemResponse]
    count: int


class ProcurementImportResponse(BaseModel):
    imported: bool
    pool_item_id: int
    created: bool


class ProcurementAnalyzeResponse(ProcurementAnalysisPayload):
    pass


class ProcurementImportPayload(SupplyImportPayload):
    pass
