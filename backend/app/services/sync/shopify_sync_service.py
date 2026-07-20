from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter
from app.core.runtime import AppError
from app.core.token_encryption import token_encryption
from app.repositories.data_connection import data_connection_repository
from app.repositories.sync_job import sync_job_repository


class ShopifySyncService:
    def __init__(self) -> None:
        self.adapter = ShopifyPlatformAdapter()

    def sync_connection(
        self,
        db: Session,
        *,
        user_id: int,
        workspace_id: int | None,
        platform: str = "shopify",
        reason: str = "manual",
        retry_count: int = 0,
    ) -> dict:
        connection = data_connection_repository.get_by_user_platform(db, user_id=user_id, platform=platform)
        if not connection or connection.status != "CONNECTED":
            raise AppError("SHOPIFY_CONNECTION_NOT_READY", "当前用户还没有可用的 Shopify 连接", "shopify_sync", 400)

        started_at = datetime.now(UTC)
        job = sync_job_repository.create(
            db,
            user_id=user_id,
            workspace_id=workspace_id,
            api_key_id=None,
            job_type="shopify_sync",
            platform="shopify",
            status="RUNNING",
            retry_count=retry_count,
            last_error=None,
            result_payload={"reason": reason},
            started_at=started_at,
            finished_at=None,
        )
        try:
            access_token = token_encryption.decrypt(connection.encrypted_access_token)
            products = self.adapter.fetch_products_with_token(access_token=access_token, shop_domain=connection.shop_domain or "")
            orders = self.adapter.fetch_orders_with_token(access_token=access_token, shop_domain=connection.shop_domain or "")
            if isinstance(products, dict) and products.get("error"):
                raise AppError(str(products.get("error") or "SHOPIFY_PRODUCTS_FAILED"), str(products.get("detail") or "Shopify 商品同步失败"), "shopify_sync", 502)
            if isinstance(orders, dict) and orders.get("error"):
                raise AppError(str(orders.get("error") or "SHOPIFY_ORDERS_FAILED"), str(orders.get("detail") or "Shopify 订单同步失败"), "shopify_sync", 502)
            customers = self._build_customers(orders or [])
            payload = {
                "products": self._normalize_products(products or []),
                "orders": self._normalize_orders(orders or []),
                "customers": customers,
                "summary": {
                    "products_count": len(products or []),
                    "orders_count": len(orders or []),
                    "customers_count": len(customers),
                },
            }
            job.status = "SUCCESS"
            job.finished_at = datetime.now(UTC)
            job.result_payload = payload
            sync_job_repository.save(db, job)
            data_connection_repository.touch_sync(
                db,
                record=connection,
                status="CONNECTED",
                last_synced_at=job.finished_at,
                last_sync_error=None,
                connection_meta={
                    **(connection.connection_meta or {}),
                    "last_sync_summary": payload["summary"],
                },
            )
            return payload
        except AppError as exc:
            job.status = "ERROR"
            job.finished_at = datetime.now(UTC)
            job.last_error = exc.message
            sync_job_repository.save(db, job)
            data_connection_repository.touch_sync(
                db,
                record=connection,
                status="ERROR",
                last_synced_at=connection.last_synced_at,
                last_sync_error=exc.message,
            )
            raise

    def retry_failed_syncs(self, db: Session, *, limit: int = 20) -> list[dict]:
        results: list[dict] = []
        for job in sync_job_repository.list_failed(db, platform="shopify", limit=limit):
            if job.user_id is None:
                continue
            try:
                payload = self.sync_connection(
                    db,
                    user_id=job.user_id,
                    workspace_id=job.workspace_id,
                    platform="shopify",
                    reason="retry",
                    retry_count=int(job.retry_count or 0) + 1,
                )
                results.append({"job_id": job.id, "status": "SUCCESS", "summary": payload.get("summary")})
            except Exception as exc:
                results.append({"job_id": job.id, "status": "ERROR", "error": str(exc)})
        return results

    def _normalize_products(self, products: list[dict]) -> list[dict]:
        return [
            {
                "title": str(item.get("title") or ""),
                "vendor": str(item.get("supplier") or item.get("vendor") or ""),
                "price": float(item.get("price") or 0),
                "inventory": int(item.get("inventory_quantity") or 0),
                "created_at": str(item.get("created_at") or ""),
            }
            for item in products
        ]

    def _normalize_orders(self, orders: list[dict]) -> list[dict]:
        return [
            {
                "order_id": str(item.get("id") or ""),
                "created_at": str(item.get("created_at") or ""),
                "total_price": float(item.get("current_total_price") or item.get("total_price") or 0),
                "currency": str(item.get("currency") or "USD"),
                "country": str((item.get("shipping_address") or {}).get("country_code") or (item.get("shipping_address") or {}).get("country") or "unknown"),
            }
            for item in orders
        ]

    def _build_customers(self, orders: list[dict]) -> list[dict]:
        customer_map: dict[str, dict] = {}
        country_counter: Counter[str] = Counter()
        for order in orders:
            customer = order.get("customer") or {}
            customer_id = str(customer.get("id") or "")
            if not customer_id:
                continue
            country = str((order.get("shipping_address") or {}).get("country_code") or (order.get("shipping_address") or {}).get("country") or "unknown")
            country_counter[country] += 1
            if customer_id not in customer_map:
                customer_map[customer_id] = {
                    "country": country,
                    "orders_count": 0,
                    "total_spent": 0.0,
                }
            customer_map[customer_id]["orders_count"] += 1
            customer_map[customer_id]["total_spent"] += float(order.get("current_total_price") or order.get("total_price") or 0)
        return list(customer_map.values())


shopify_sync_service = ShopifySyncService()
