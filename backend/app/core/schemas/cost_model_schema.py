from __future__ import annotations

from app.core.schemas.common import BaseDataSchema


class CostModelSchema(BaseDataSchema):
    product_cost: float
    shipping_cost: float
    platform_fee: float
    ads_cost: float
    packaging_cost: float
    total_cost: float
    currency: str
