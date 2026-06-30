from __future__ import annotations

from app.core.schemas.common import BaseDataSchema


class SupplierOfferSchema(BaseDataSchema):
    id: str
    product_keyword: str
    supplier_name: str
    platform: str
    price: float | None = None
    moq: int | None = None
    shipping_time: str | None = None
    location: str | None = None
    rating: float | None = None
    match_score: float
    profit_estimate: float | None = None
    supplier_title: str | None = None
    supplier_url: str | None = None
    availability: str | None = None
    currency: str | None = None
    product_id: int | None = None
