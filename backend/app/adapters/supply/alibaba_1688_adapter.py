from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote

import httpx

from app.adapters.supply.base import SupplyAdapterBase
from app.adapters.supply.supply_base import SupplyDataAdapter
from app.core.contracts import SupplyOffer


@dataclass(frozen=True)
class AlibabaQuery:
    keyword: str
    category: str | None = None
    target_price: float | None = None
    region: str = "CN"


class Alibaba1688APIClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("ALIBABA1688_API_BASE_URL", "").strip()
        self.token = os.getenv("ALIBABA1688_API_TOKEN", "").strip()

    def configured(self) -> bool:
        return bool(self.base_url and self.token)

    async def search_products(self, query: AlibabaQuery) -> list[dict]:
        if not self.configured():
            return []
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(
                    f"{self.base_url.rstrip('/')}/products/search",
                    params={
                        "keyword": query.keyword,
                        "category": query.category,
                        "target_price": query.target_price,
                        "region": query.region,
                    },
                    headers={"Authorization": f"Bearer {self.token}"},
                )
            if response.status_code != 200:
                return []
            payload = response.json()
            items = payload.get("items")
            return items if isinstance(items, list) else []
        except Exception:
            return []


class Alibaba1688Provider(SupplyDataAdapter):
    source_name = "alibaba_1688_provider"

    def __init__(self) -> None:
        self.api_client = Alibaba1688APIClient()

    async def fetch(
        self,
        keyword: str,
        target_market: str,
        category: str | None = None,
        expected_price: float | None = None,
        quantity: int = 100,
    ) -> dict:
        del quantity
        query = AlibabaQuery(
            keyword=keyword.strip(),
            category=category,
            target_price=expected_price,
            region=target_market or "CN",
        )
        api_payload = await self.fetch_api(query)
        if api_payload.get("data", {}).get("suppliers"):
            return api_payload
        return await self.fetch_public_page(query)

    async def fetch_api(self, query: AlibabaQuery) -> dict:
        products = await self.api_client.search_products(query)
        suppliers = [self._normalize_product(item, source_type="alibaba_api", confidence_score=0.92) for item in products]
        suppliers = [item for item in suppliers if item]
        return self._envelope(
            source="alibaba_api" if self.api_client.configured() else "alibaba_api_unconfigured",
            data={
                "keyword": query.keyword,
                "suppliers": suppliers,
                "source_type": "alibaba_api",
            },
            confidence=0.92 if suppliers else 0.0,
            is_mock=False,
            source_status="live" if suppliers else ("not_configured" if not self.api_client.configured() else "empty"),
        )

    async def fetch_public_page(self, query: AlibabaQuery) -> dict:
        search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote(query.keyword)}"
        try:
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(search_url)
            text = response.text.lower()
            login_required = "login.1688.com" in text or "redirecttype=topredirect" in text
            if response.status_code != 200:
                return self._envelope(
                    source="alibaba_public_page",
                    data={"keyword": query.keyword, "suppliers": [], "search_url": search_url},
                    confidence=0.0,
                    is_mock=True,
                    source_status="failed",
                )
            if login_required:
                return self._envelope(
                    source="alibaba_public_page",
                    data={
                        "keyword": query.keyword,
                        "suppliers": [],
                        "search_url": search_url,
                        "message": "1688 公开页当前需要登录，系统未绕过登录。",
                    },
                    confidence=0.15,
                    is_mock=True,
                    source_status="public_login_required",
                )
            return self._envelope(
                source="alibaba_public_page",
                data={
                    "keyword": query.keyword,
                    "suppliers": [
                        {
                            "supplier_name": "1688公开搜索入口",
                            "product_title": f"{query.keyword} 公开搜索入口",
                            "product_url": search_url,
                            "images": [],
                            "price_range": {"min": 0.0, "max": 0.0, "currency": "CNY"},
                            "min_order_quantity": 0,
                            "supplier_location": None,
                            "factory_level": "",
                            "certification": "",
                            "delivery_time": None,
                            "source_type": "public_page",
                            "confidence_score": 0.2,
                            "is_mock": True,
                            "availability": "public_page_only",
                        }
                    ],
                    "search_url": search_url,
                },
                confidence=0.2,
                is_mock=True,
                source_status="public_partial",
            )
        except Exception as exc:
            return self._envelope(
                source="alibaba_public_page",
                data={"keyword": query.keyword, "suppliers": [], "search_url": search_url, "message": str(exc)},
                confidence=0.0,
                is_mock=True,
                source_status="failed",
            )

    def _normalize_product(self, item: dict, *, source_type: str, confidence_score: float) -> dict | None:
        supplier_name = str(item.get("supplier_name") or item.get("supplier") or "").strip()
        product_title = str(item.get("product_title") or item.get("title") or "").strip()
        if not supplier_name and not product_title:
            return None
        price_min = float(item.get("price_min") or item.get("min_price") or item.get("price") or 0)
        price_max = float(item.get("price_max") or item.get("max_price") or price_min or 0)
        currency = str(item.get("currency") or "CNY")
        return {
            "supplier_name": supplier_name or "未命名供应商",
            "product_title": product_title or "未命名商品",
            "product_url": item.get("product_url") or item.get("url") or "",
            "images": list(item.get("images") or []),
            "price_range": {"min": price_min, "max": price_max, "currency": currency},
            "min_order_quantity": int(item.get("min_order_quantity") or item.get("moq") or 0),
            "supplier_location": item.get("supplier_location") or item.get("location"),
            "factory_level": str(item.get("factory_level") or item.get("factory_info") or ""),
            "certification": str(item.get("certification") or ""),
            "delivery_time": item.get("delivery_time"),
            "source_type": source_type,
            "confidence_score": confidence_score,
            "availability": str(item.get("availability") or "available"),
            "transaction_score": float(item.get("transaction_score") or 0),
            "factory_score": float(item.get("factory_score") or 0),
            "feedback_score": float(item.get("feedback_score") or 0),
        }


class Alibaba1688Adapter(SupplyAdapterBase):
    adapter_name = "1688_v2_provider"
    supported_channels = ("amazon", "shopify", "shopee", "tiktok", "1688")

    def __init__(self) -> None:
        self.provider = Alibaba1688Provider()

    def search_supply(self, *, keyword: str, market: str) -> list[SupplyOffer]:
        del market
        return [
            SupplyOffer(
                source="1688_v2_provider",
                supplier_id=f"public:{keyword}",
                supplier_name="1688 供应入口",
                keyword=keyword,
                product_title=f"{keyword} 供应入口",
                price=0.0,
                min_order_qty=0,
                rating=0.0,
                shipping_days=0,
            )
        ]
