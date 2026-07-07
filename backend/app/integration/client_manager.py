from __future__ import annotations

from dataclasses import dataclass

from app.adapters.execution.registry import execution_adapter_registry
from app.adapters.market.registry import market_adapter_registry
from app.adapters.supply.registry import supply_adapter_registry


@dataclass(frozen=True)
class ClientRoute:
    market_client: object
    supply_client: object
    execution_client: object
    ordered_layers: list[str]


class ClientManager:
    def resolve_route(self, *, market: str, channel: str) -> ClientRoute:
        market_client = market_adapter_registry.resolve(market)
        supply_client = supply_adapter_registry.resolve(market)
        execution_client = execution_adapter_registry.resolve(channel)
        return ClientRoute(
            market_client=market_client,
            supply_client=supply_client,
            execution_client=execution_client,
            ordered_layers=["market", "supply", "execution"],
        )

    def get_market_client(self, *, market: str):
        return self.resolve_route(market=market, channel="shopify").market_client

    def get_supply_client(self, *, market: str):
        return self.resolve_route(market=market, channel="shopify").supply_client

    def get_execution_client(self, *, channel: str):
        return execution_adapter_registry.resolve(channel)

    def ensure_execution_order(self, *, completed_layers: list[str]) -> None:
        normalized = completed_layers[:]
        if "execution" in normalized and ("market" not in normalized or "supply" not in normalized):
            raise ValueError("执行层不能跳过市场层和供货层")


client_manager = ClientManager()
