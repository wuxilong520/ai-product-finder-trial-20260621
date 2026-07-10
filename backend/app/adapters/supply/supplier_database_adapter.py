from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.supply.supply_base import SupplyDataAdapter
from app.models.supplier import Supplier, SupplierProduct


class SupplierDatabaseAdapter(SupplyDataAdapter):
    source_name = "supplier_database"

    def __init__(self, db: Session) -> None:
        self.db = db

    async def fetch(
        self,
        keyword: str,
        target_market: str,
        category: str | None = None,
        expected_price: float | None = None,
        quantity: int = 100,
    ) -> dict:
        return await self.fetch_by_source_types(
            keyword=keyword,
            source_types=["cache_database", "cached", "merchant_authorized", "browser_extension", "csv_import", "manual_input"],
            category=category,
        )

    async def fetch_by_source_types(
        self,
        *,
        keyword: str,
        source_types: list[str],
        category: str | None = None,
    ) -> dict:
        cutoff = datetime.now(UTC) - timedelta(days=30)
        stmt = (
            select(Supplier, SupplierProduct)
            .join(SupplierProduct, SupplierProduct.supplier_id == Supplier.id)
            .where(SupplierProduct.keyword == keyword.strip())
            .where(Supplier.last_verified_time >= cutoff)
        )
        if category:
            stmt = stmt.where(Supplier.product_category == category)
        if source_types:
            stmt = stmt.where(Supplier.source_type.in_(source_types))
        rows = self.db.execute(stmt).all()
        suppliers = []
        for supplier, product in rows[:12]:
            suppliers.append(
                {
                    "supplier_name": supplier.name,
                    "platform": supplier.platform,
                    "supplier_type": supplier.supplier_type,
                    "supplier_location": supplier.location,
                    "product_category": supplier.product_category,
                    "product_title": product.product_title,
                    "images": list(product.images or ([] if not product.product_image else [product.product_image])),
                    "product_url": product.product_url,
                    "price_range": {
                        "min": float(product.price_min or 0),
                        "max": float(product.price_max or 0),
                        "currency": product.currency or "CNY",
                    },
                    "min_order_quantity": int(supplier.min_order_quantity or 0),
                    "transaction_score": float(supplier.transaction_score or 0),
                    "factory_score": float(supplier.factory_score or 0),
                    "trust_score": float(supplier.trust_score or 0),
                    "factory_level": product.factory_info or "",
                    "certification": supplier.certification or "",
                    "delivery_time": supplier.delivery_time_days,
                    "feedback_score": float(supplier.trust_score or 0),
                    "data_source": supplier.source_type or product.source_type or "cache_database",
                    "source_type": supplier.source_type or product.source_type or "cache_database",
                    "confidence_score": float(product.confidence_score or supplier.confidence_score or 0.74),
                    "supplier_verified": bool(supplier.supplier_verified),
                    "verification_status": supplier.verification_status or "unverified",
                    "delivery_score": float(supplier.delivery_score or 0),
                    "price_history": list(supplier.price_history or []),
                    "is_mock": False,
                    "search_url": product.product_url,
                    "last_verified_time": supplier.last_verified_time.isoformat() if supplier.last_verified_time else None,
                    "availability": "available",
                    "feedback_status": supplier.last_feedback,
                }
            )
        current_source = source_types[0] if source_types else "cache_database"
        return self._envelope(
            source=f"{self.source_name}_{current_source}_{'cached' if suppliers else 'empty'}",
            data={
                "keyword": keyword,
                "suppliers": suppliers,
                "platform": "supplier_database",
                "data_source": current_source if suppliers else "unavailable",
            },
            confidence=0.74 if suppliers else 0.0,
            is_mock=False,
            source_status="cached" if suppliers else "unavailable",
        )
