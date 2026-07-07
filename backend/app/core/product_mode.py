from __future__ import annotations

from enum import Enum


class ProductMode(str, Enum):
    DEMO = "demo_mode"
    BETA = "beta_mode"
    PRODUCTION = "production_mode"


class ProductModeResolver:
    def resolve(self, *, commercial_ready: bool, scale_ready: bool) -> str:
        if not commercial_ready:
            return ProductMode.DEMO.value
        if commercial_ready and not scale_ready:
            return ProductMode.BETA.value
        return ProductMode.PRODUCTION.value


product_mode_resolver = ProductModeResolver()
