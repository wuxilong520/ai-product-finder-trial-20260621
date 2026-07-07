from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.contracts import SupplyOffer


class SupplyAdapterBase(ABC):
    adapter_name: str
    supported_channels: tuple[str, ...]

    @abstractmethod
    def search_supply(self, *, keyword: str, market: str) -> list[SupplyOffer]:
        raise NotImplementedError
