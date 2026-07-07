from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ApiEnvelope(BaseModel):
    success: bool = True
    data: dict
    meta: dict = Field(default_factory=dict)


class AnalyzeV1Request(BaseModel):
    keyword: str = Field(..., min_length=1)
    market: Literal["amazon", "shopify", "shopee", "tiktok"] = "amazon"


class DecisionV1Request(BaseModel):
    keyword: str = Field(..., min_length=1)
    market: Literal["amazon", "shopify", "shopee", "tiktok"] = "amazon"
    target_margin_rate: float = 0.3
    strategy_mode: Literal["sourcing", "listing", "scaling"] = "sourcing"
    business_constraints: dict = Field(default_factory=dict)


class ListingV1Request(BaseModel):
    keyword: str = Field(..., min_length=1)
    market: Literal["amazon", "shopify", "shopee", "tiktok"] = "amazon"
    channel: Literal["shopify", "amazon", "shopee", "tiktok"] = "shopify"


class PublishV1Request(BaseModel):
    keyword: str = Field(..., min_length=1)
    market: Literal["amazon", "shopify", "shopee", "tiktok"] = "amazon"
    channel: Literal["shopify", "amazon", "shopee", "tiktok"] = "shopify"
    shop_domain: str = Field(..., min_length=1)
    oauth_code: str | None = None
