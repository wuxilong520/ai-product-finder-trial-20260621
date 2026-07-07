from __future__ import annotations

from app.adapters.platform.alibaba_1688_adapter import Alibaba1688PlatformAdapter
from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter


class PlatformRouter:
    def __init__(self) -> None:
        self.shopify = ShopifyPlatformAdapter()
        self.alibaba_1688 = Alibaba1688PlatformAdapter()
        self.real_data_priority_mode = ['real', 'partial', 'mock']

    def get_shopify_candidates(self, keyword: str) -> list[dict]:
        return self._prioritize(self.shopify.search_product(keyword))

    def get_alibaba_suppliers(self, keyword: str) -> list[dict]:
        return self._prioritize(self.alibaba_1688.search_product(keyword))

    def _prioritize(self, items: list[dict]) -> list[dict]:
        rank = {name: index for index, name in enumerate(self.real_data_priority_mode)}
        return sorted(items, key=lambda item: rank.get(item.get("data_source_type", "mock"), 99))

    def normalize_product_data(self, record: dict) -> dict:
        return {
            "title": str(record.get("title") or ""),
            "price": float(record.get("price") or 0),
            "currency": str(record.get("currency") or "CNY"),
            "supplier": str(record.get("supplier") or ""),
            "availability": bool(record.get("availability", False)),
            "shipping_time": str(record.get("shipping_time") or ""),
            "raw_platform": str(record.get("raw_platform") or "unknown"),
            "is_real_platform_data": bool(record.get("is_real_platform_data", False)),
            "data_source_type": str(record.get("data_source_type") or "mock"),
            **({"product_id": record.get("product_id")} if record.get("product_id") else {}),
            **({"moq": record.get("moq")} if record.get("moq") is not None else {}),
            **({"search_url": record.get("search_url")} if record.get("search_url") else {}),
        }

    def decide_platform_target(self, *, action_level: str) -> str:
        normalized = str(action_level).upper()
        if normalized == 'AUTO_LIST':
            return 'shopify'
        if normalized == 'TEST':
            return 'shopify_draft'
        return 'none'

    def execute_platform_action(self, *, action_level: str, product: dict) -> dict:
        target = self.decide_platform_target(action_level=action_level)
        normalized = self.normalize_product_data(product)
        if target == 'shopify':
            result = self.shopify.publish_product(normalized)
            return {**result, 'execution_target_platform': 'shopify'}
        if target == 'shopify_draft':
            result = self.shopify.publish_product(normalized)
            result['publish_decision'] = 'draft_only'
            return {**result, 'execution_target_platform': 'shopify'}
        return {
            'status': 'blocked',
            'publish_decision': 'no_publish',
            'execution_target_platform': 'none',
            'product': normalized,
            'is_real_platform_data': False,
        }

platform_router = PlatformRouter()
