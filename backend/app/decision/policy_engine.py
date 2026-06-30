from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DecisionPolicy:
    market_type: str
    supplier_strategy: str
    cost_mode: str
    decision_mode: str
    provider_routing: dict[str, str]
    scoring_weights: dict[str, float]
    cost_model_mode: str
    pipeline_depth: str


class PolicyEngine:
    MARKET_PROVIDER_MAP = {
        "amazon": "AmazonProvider",
        "1688": "AlibabaProvider",
        "shopify": "ShopifyProvider",
        "shopee": "ShopifyProvider",
    }

    SUPPLIER_WEIGHTS = {
        "cheapest": {"price": 0.6, "rating": 0.2, "speed": 0.2},
        "quality": {"price": 0.2, "rating": 0.6, "speed": 0.2},
        "balanced": {"price": 0.4, "rating": 0.4, "speed": 0.2},
    }

    @classmethod
    def build(cls, task_input: dict | None) -> DecisionPolicy:
        payload = task_input or {}
        market_type = str(payload.get("market_type") or "amazon").lower()
        supplier_strategy = str(payload.get("supplier_strategy") or "balanced").lower()
        cost_mode = str(payload.get("cost_mode") or "estimated").lower()
        decision_mode = str(payload.get("decision_mode") or "deep").lower()

        provider_name = cls.MARKET_PROVIDER_MAP.get(market_type, "AmazonProvider")
        weights = cls.SUPPLIER_WEIGHTS.get(supplier_strategy, cls.SUPPLIER_WEIGHTS["balanced"])

        return DecisionPolicy(
            market_type=market_type,
            supplier_strategy=supplier_strategy,
            cost_mode=cost_mode,
            decision_mode=decision_mode,
            provider_routing={
                "market": provider_name,
                "supplier": supplier_strategy,
                "market_provider": provider_name,
                "supplier_provider": {
                    "cheapest": "LowestPriceSupplierProvider",
                    "quality": "HighRatingSupplierProvider",
                    "balanced": "MixedSupplierProvider",
                }.get(supplier_strategy, "MixedSupplierProvider"),
                "cost_provider": "RealCostAPIProvider" if cost_mode == "strict" else "HeuristicCostProvider",
            },
            scoring_weights=weights,
            cost_model_mode="real_api_cost" if cost_mode == "strict" else "heuristic_model",
            pipeline_depth="shallow" if decision_mode == "fast" else "full",
        )


policy_engine = PolicyEngine()
