from __future__ import annotations

from app.decision import DecisionPolicy
from app.core.schemas import CostModelSchema, SupplierOfferSchema
from app.providers import LogisticsAPIProvider, MockCostProvider


class CostSyncPipeline:
    def __init__(self) -> None:
        self.provider = MockCostProvider()
        self.future_provider = LogisticsAPIProvider()

    def sync_cost(
        self,
        *,
        selling_price: float,
        currency: str,
        suppliers: list[SupplierOfferSchema],
        package_weight_kg: float = 0.45,
        policy: DecisionPolicy | None = None,
    ) -> CostModelSchema:
        provider_name = "HeuristicCostProvider"
        if policy:
            provider_name = policy.provider_routing.get("cost_provider") or provider_name
        provider = self.future_provider if provider_name == "RealCostAPIProvider" else self.provider
        cost = provider.calculate_cost(
            {
                "selling_price": selling_price,
                "currency": currency,
                "suppliers": suppliers,
                "package_weight_kg": package_weight_kg,
            }
        )
        if provider_name == "RealCostAPIProvider":
            cost.truth_level = "semi_real"
            cost.source_type = "api"
            cost.provider_name = provider_name
            cost.transform_steps = [*list(cost.transform_steps or []), "strict_cost_mode", "provider_router_cost_select"]
        else:
            cost.provider_name = provider_name
            cost.source_type = "estimated"
            cost.transform_steps = [*list(cost.transform_steps or []), "estimated_cost_mode", "provider_router_cost_select"]
        cost.lineage_chain = [*list(cost.lineage_chain or []), provider_name]
        return cost


cost_sync_pipeline = CostSyncPipeline()
