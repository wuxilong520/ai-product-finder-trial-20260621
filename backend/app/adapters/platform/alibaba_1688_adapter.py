from __future__ import annotations

from urllib.parse import quote

from app.adapters.platform.base_platform import PlatformAdapter


class Alibaba1688PlatformAdapter(PlatformAdapter):
    adapter_name = "alibaba_1688_platform"

    def search_product(self, keyword: str):
        real_items = self.real_supplier_search(keyword)
        if real_items:
            return real_items
        return [
            {
                "title": f"{keyword} 1688 工厂基础款",
                "price": 16.8,
                "currency": "CNY",
                "supplier": "义乌优选工厂",
                "availability": True,
                "shipping_time": "6 days",
                "raw_platform": "1688",
                "product_id": "1688-A1001",
                "moq": 50,
                "is_real_platform_data": False,
                "data_source_type": "mock",
            },
            {
                "title": f"{keyword} 1688 升级款",
                "price": 19.5,
                "currency": "CNY",
                "supplier": "杭州稳定供货商",
                "availability": True,
                "shipping_time": "4 days",
                "raw_platform": "1688",
                "product_id": "1688-A1002",
                "moq": 30,
                "is_real_platform_data": False,
                "data_source_type": "mock",
            },
        ]

    def get_price(self, product_id: str):
        catalog = {item['product_id']: item for item in self.search_product('wireless earbuds')}
        item = catalog.get(product_id) or self.search_product('sample')[0]
        return item

    def publish_product(self, product: dict):
        return {
            "status": "blocked",
            "publish_decision": "supplier_only_no_publish",
            "platform": "1688",
            "product": product,
            "is_real_platform_data": False,
            "data_source_type": "mock",
        }

    def get_inventory(self, product_id: str):
        return {
            "product_id": product_id,
            "inventory": 9999,
            "availability": True,
            "raw_platform": "1688",
            "is_real_platform_data": False,
            "data_source_type": "mock",
        }

    def supplier_matching(self, keyword: str):
        return self.search_product(keyword)

    def cost_estimation(self, keyword: str):
        items = self.search_product(keyword)
        best = min(items, key=lambda item: item['price'])
        return {
            "keyword": keyword,
            "cost_estimate": best['price'],
            "currency": best['currency'],
            "supplier": best['supplier'],
            "moq": best['moq'],
            "is_real_platform_data": False,
        }

    def detect_moq(self, product_id: str):
        item = self.get_price(product_id)
        return {
            "product_id": product_id,
            "moq": item.get('moq', 0),
            "is_real_platform_data": False,
        }


    def real_supplier_search(self, keyword: str) -> list[dict]:
        encoded = quote(keyword)
        return [
            {
                'title': f'{keyword} 1688 实时搜索入口',
                'price': 0.0,
                'currency': 'CNY',
                'supplier': '1688 Search',
                'availability': True,
                'shipping_time': 'unknown',
                'raw_platform': '1688',
                'product_id': f'1688-search-{encoded}',
                'moq': 0,
                'is_real_platform_data': False,
                'data_source_type': 'partial',
                'search_url': f'https://s.1688.com/selloffer/offer_search.htm?keywords={encoded}',
            }
        ]

    def real_cost_estimation(self, keyword: str):
        items = self.search_product(keyword)
        ranked = self.rank_suppliers(items)
        best = ranked[0]
        return {
            'keyword': keyword,
            'cost_estimate': float(best.get('price') or 0),
            'currency': best.get('currency') or 'CNY',
            'supplier': best.get('supplier') or '',
            'moq': best.get('moq') or 0,
            'is_real_platform_data': bool(best.get('is_real_platform_data', False)),
            'data_source_type': best.get('data_source_type', 'mock'),
        }

    def real_moq_detection(self, product_id: str):
        item = self.get_price(product_id)
        return {
            'product_id': product_id,
            'moq': item.get('moq', 0),
            'is_real_platform_data': bool(item.get('is_real_platform_data', False)),
            'data_source_type': item.get('data_source_type', 'mock'),
        }

    def rank_suppliers(self, items: list[dict]) -> list[dict]:
        return sorted(items, key=lambda item: (item.get('price') or 999999, -(1 if item.get('data_source_type') == 'real' else 0)))
