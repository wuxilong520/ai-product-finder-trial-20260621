from __future__ import annotations

from app.adapters.execution.base import ExecutionAdapterBase
from app.adapters.execution.future_execution_adapters import AmazonExecutionAdapter, ShopeeExecutionAdapter, TikTokExecutionAdapter
from app.adapters.execution.shopify_adapter import ShopifyExecutionAdapter


class ExecutionAdapterRegistry:
    def __init__(self):
        self._adapters: list[ExecutionAdapterBase] = [
            ShopifyExecutionAdapter(),
            AmazonExecutionAdapter(),
            ShopeeExecutionAdapter(),
            TikTokExecutionAdapter(),
        ]

    def resolve(self, channel: str) -> ExecutionAdapterBase:
        normalized = channel.strip().lower()
        for adapter in self._adapters:
            if normalized in adapter.supported_channels:
                return adapter
        return ShopifyExecutionAdapter()


execution_adapter_registry = ExecutionAdapterRegistry()
