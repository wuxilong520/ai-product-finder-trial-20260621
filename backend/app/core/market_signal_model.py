from __future__ import annotations

from pydantic import BaseModel, Field


class MarketSignalModel(BaseModel):
    keyword: str
    region: str
    amazon_signal: dict = Field(default_factory=dict)
    tiktok_signal: dict = Field(default_factory=dict)
    meta_signal: dict = Field(default_factory=dict)
    seo_signal: dict = Field(default_factory=dict)
    shopify_signal: dict = Field(default_factory=dict)
    data_quality_score: float = 0.0
    real_data_ratio: float = 0.0
