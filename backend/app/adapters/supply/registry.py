from __future__ import annotations

from app.adapters.supply.alibaba_1688_adapter import Alibaba1688Adapter
from app.adapters.supply.base import SupplyAdapterBase


class SupplyAdapterRegistry:
    def __init__(self):
        self._adapters: list[SupplyAdapterBase] = [Alibaba1688Adapter()]

    def resolve(self, market: str) -> SupplyAdapterBase:
        normalized = market.strip().lower()
        for adapter in self._adapters:
            if normalized in adapter.supported_channels:
                return adapter
        return Alibaba1688Adapter()


supply_adapter_registry = SupplyAdapterRegistry()
