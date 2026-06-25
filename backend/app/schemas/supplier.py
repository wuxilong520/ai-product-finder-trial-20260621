from pydantic import BaseModel, Field


class SupplierMatchRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="供应链匹配关键词", examples=["air fryer"])


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


class SupplierMatchResponse(BaseModel):
    suppliers: list[SupplierMatchItem]
