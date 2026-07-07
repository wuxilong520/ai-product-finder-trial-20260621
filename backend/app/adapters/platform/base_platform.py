from __future__ import annotations

from abc import ABC, abstractmethod


class PlatformAdapter(ABC):
    adapter_name: str

    @abstractmethod
    def search_product(self, keyword: str):
        raise NotImplementedError

    @abstractmethod
    def get_price(self, product_id: str):
        raise NotImplementedError

    @abstractmethod
    def publish_product(self, product: dict):
        raise NotImplementedError

    @abstractmethod
    def get_inventory(self, product_id: str):
        raise NotImplementedError
