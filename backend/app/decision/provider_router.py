from __future__ import annotations

from dataclasses import dataclass

from app.decision.policy_engine import DecisionPolicy


@dataclass
class ProviderRouting:
    market_provider: str
    supplier_provider: str
    cost_provider: str
    routing_metadata: dict[str, str]


class ProviderRouter:
    MARKET_PROVIDER_MAP = {
        "amazon": "AmazonProvider",
        "1688": "AlibabaProvider",
        "shopify": "ShopifyProvider",
        "shopee": "ShopifyProvider",
    }

    SUPPLIER_PROVIDER_MAP = {
        "cheapest": "LowestPriceSupplierProvider",
        "quality": "HighRatingSupplierProvider",
        "balanced": "MixedSupplierProvider",
    }

    COST_PROVIDER_MAP = {
        "strict": "RealCostAPIProvider",
        "estimated": "HeuristicCostProvider",
    }

    @classmethod
    def build(cls, policy: DecisionPolicy | None) -> ProviderRouting:
        if policy is None:
            return ProviderRouting(
                market_provider="AmazonProvider",
                supplier_provider="MixedSupplierProvider",
                cost_provider="HeuristicCostProvider",
                routing_metadata={
                    "market_type": "amazon",
                    "supplier_strategy": "balanced",
                    "cost_mode": "estimated",
                    "decision_mode": "deep",
                    "pipeline_depth": "full",
                    "market_provider": "AmazonProvider",
                    "supplier_provider": "MixedSupplierProvider",
                    "cost_provider": "HeuristicCostProvider",
                },
            )

        market_provider = cls.MARKET_PROVIDER_MAP.get(policy.market_type, "AmazonProvider")
        supplier_provider = cls.SUPPLIER_PROVIDER_MAP.get(policy.supplier_strategy, "MixedSupplierProvider")
        cost_provider = cls.COST_PROVIDER_MAP.get(policy.cost_mode, "HeuristicCostProvider")

        return ProviderRouting(
            market_provider=market_provider,
            supplier_provider=supplier_provider,
            cost_provider=cost_provider,
            routing_metadata={
                "market_type": policy.market_type,
                "supplier_strategy": policy.supplier_strategy,
                "cost_mode": policy.cost_mode,
                "decision_mode": policy.decision_mode,
                "pipeline_depth": policy.pipeline_depth,
                "market_provider": market_provider,
                "supplier_provider": supplier_provider,
                "cost_provider": cost_provider,
            },
        )


provider_router = ProviderRouter()
