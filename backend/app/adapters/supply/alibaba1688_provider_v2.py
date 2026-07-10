from __future__ import annotations

from sqlalchemy.orm import Session

from app.adapters.supply.alibaba_1688_adapter import Alibaba1688APIClient, AlibabaQuery
from app.adapters.supply.supplier_database_adapter import SupplierDatabaseAdapter
from app.adapters.supply.supply_base import SupplyDataAdapter


class Alibaba1688ProviderV2(SupplyDataAdapter):
    source_name = "alibaba1688_provider_v2"

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
        return await self.fetch_api(query)

    async def fetch_api(self, query: AlibabaQuery) -> dict:
        products = await self.api_client.search_products(query)
        suppliers = [self._normalize_api_product(item, source_type="1688_api", source_status="real") for item in products]
        suppliers = [item for item in suppliers if item]
        return self._envelope(
            source="alibaba_1688_api",
            data={"keyword": query.keyword, "suppliers": suppliers},
            confidence=0.92 if suppliers else 0.0,
            is_mock=False,
            source_status="real" if suppliers else "unavailable",
        )

    async def fetch_merchant_authorized(self, db: Session, query: AlibabaQuery) -> dict:
        adapter = SupplierDatabaseAdapter(db)
        payload = await adapter.fetch_by_source_types(
            keyword=query.keyword,
            source_types=["merchant_authorized"],
            category=query.category,
        )
        return self._retag_payload(payload, source="merchant_authorized", source_status="real", confidence=0.9)

    async def fetch_browser_extension(self, db: Session, query: AlibabaQuery) -> dict:
        adapter = SupplierDatabaseAdapter(db)
        payload = await adapter.fetch_by_source_types(
            keyword=query.keyword,
            source_types=["browser_extension"],
            category=query.category,
        )
        return self._retag_payload(payload, source="browser_extension", source_status="real", confidence=0.88)

    async def fetch_user_upload(self, db: Session, query: AlibabaQuery) -> dict:
        adapter = SupplierDatabaseAdapter(db)
        csv_payload = await adapter.fetch_by_source_types(
            keyword=query.keyword,
            source_types=["csv_import"],
            category=query.category,
        )
        manual_payload = await adapter.fetch_by_source_types(
            keyword=query.keyword,
            source_types=["manual_input"],
            category=query.category,
        )
        merged = list(csv_payload.get("data", {}).get("suppliers", [])) + list(manual_payload.get("data", {}).get("suppliers", []))
        return self._envelope(
            source="user_upload",
            data={"keyword": query.keyword, "suppliers": [self._normalize_db_item(item, "1688_import", "partial") for item in merged]},
            confidence=0.76 if merged else 0.0,
            is_mock=False,
            source_status="partial" if merged else "unavailable",
        )

    async def fetch_cache(self, db: Session, query: AlibabaQuery) -> dict:
        adapter = SupplierDatabaseAdapter(db)
        payload = await adapter.fetch_by_source_types(
            keyword=query.keyword,
            source_types=["cache_database", "cached"],
            category=query.category,
        )
        return self._retag_payload(payload, source="cache_database", source_status="cached", confidence=0.62)

    def _retag_payload(self, payload: dict, *, source: str, source_status: str, confidence: float) -> dict:
        suppliers = [self._normalize_db_item(item, source, source_status) for item in payload.get("data", {}).get("suppliers", [])]
        suppliers = [item for item in suppliers if item]
        return self._envelope(
            source=source,
            data={"keyword": payload.get("data", {}).get("keyword"), "suppliers": suppliers},
            confidence=confidence if suppliers else 0.0,
            is_mock=False,
            source_status=source_status if suppliers else "unavailable",
        )

    def _normalize_db_item(self, item: dict, source_type: str, source_status: str) -> dict:
        price_range = item.get("price_range") or {}
        price_min = float(price_range.get("min") or item.get("price_min") or 0)
        price_max = float(price_range.get("max") or item.get("price_max") or price_min or 0)
        price = round((price_min + price_max) / 2, 2) if (price_min or price_max) else 0.0
        certification = str(item.get("certification") or "")
        verified = bool(item.get("supplier_verified")) or source_status == "real" or bool(certification)
        delivery_score = float(item.get("delivery_score") or 0)
        if delivery_score <= 0:
            delivery_value = item.get("delivery_time")
            if isinstance(delivery_value, int) and delivery_value > 0:
                delivery_score = max(35.0, min(95.0, 100 - delivery_value * 4))
            else:
                delivery_score = 45.0
        return {
            "supplier_name": item.get("supplier_name"),
            "product_title": item.get("product_title"),
            "product_url": item.get("product_url") or item.get("search_url") or "",
            "images": list(item.get("images") or []),
            "price": price,
            "price_range": {"min": price_min, "max": price_max, "currency": str(price_range.get("currency") or item.get("currency") or "CNY")},
            "moq": int(item.get("min_order_quantity") or item.get("moq") or 0),
            "min_order_quantity": int(item.get("min_order_quantity") or item.get("moq") or 0),
            "supplier_location": item.get("supplier_location") or item.get("location"),
            "factory_level": str(item.get("factory_level") or item.get("factory_info") or ""),
            "factory_score": float(item.get("factory_score") or 0),
            "certification": certification,
            "delivery_time": item.get("delivery_time"),
            "delivery_score": round(delivery_score, 2),
            "source_type": source_type,
            "source_status": source_status,
            "confidence_score": float(item.get("confidence_score") or 0),
            "verification_status": "verified" if verified else "unverified",
            "supplier_verified": verified,
            "price_history": list(item.get("price_history") or []),
            "availability": str(item.get("availability") or "available"),
            "is_mock": False,
        }

    def _normalize_api_product(self, item: dict, source_type: str, source_status: str) -> dict | None:
        supplier_name = str(item.get("supplier_name") or item.get("supplier") or "").strip()
        product_title = str(item.get("product_title") or item.get("title") or "").strip()
        if not supplier_name and not product_title:
            return None
        price_min = float(item.get("price_min") or item.get("min_price") or item.get("price") or 0)
        price_max = float(item.get("price_max") or item.get("max_price") or price_min or 0)
        price = round((price_min + price_max) / 2, 2) if (price_min or price_max) else 0.0
        factory_score = float(item.get("factory_score") or item.get("transaction_score") or 0)
        delivery_score = float(item.get("delivery_score") or 65.0)
        certification = str(item.get("certification") or "")
        return {
            "supplier_name": supplier_name or "未命名供应商",
            "product_title": product_title or "未命名商品",
            "product_url": item.get("product_url") or item.get("url") or "",
            "images": list(item.get("images") or []),
            "price": price,
            "price_range": {"min": price_min, "max": price_max, "currency": str(item.get("currency") or "CNY")},
            "moq": int(item.get("min_order_quantity") or item.get("moq") or 0),
            "min_order_quantity": int(item.get("min_order_quantity") or item.get("moq") or 0),
            "supplier_location": item.get("supplier_location") or item.get("location"),
            "factory_level": str(item.get("factory_level") or item.get("factory_info") or ""),
            "factory_score": factory_score,
            "certification": certification,
            "delivery_time": item.get("delivery_time"),
            "delivery_score": delivery_score,
            "source_type": source_type,
            "source_status": source_status,
            "confidence_score": 0.92,
            "verification_status": "verified" if certification or factory_score >= 70 else "pending",
            "supplier_verified": bool(certification) or factory_score >= 70,
            "price_history": [],
            "availability": str(item.get("availability") or "available"),
            "is_mock": False,
        }
