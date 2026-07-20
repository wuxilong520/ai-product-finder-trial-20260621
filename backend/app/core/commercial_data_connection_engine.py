from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.adapters.platform.shopify_adapter import ShopifyPlatformAdapter
from app.core.runtime import AppError
from app.core.token_encryption import token_encryption
from app.repositories.data_connection import data_connection_repository
from app.services.sync.shopify_sync_service import shopify_sync_service
from app.services.oauth.shopify_oauth_service import shopify_oauth_service


class CommercialDataConnectionEngine:
    def __init__(self) -> None:
        self.shopify = ShopifyPlatformAdapter()

    def _normalize_status(self, value: str | None) -> str:
        text = str(value or "").strip().upper()
        return text or "DISCONNECTED"

    def list_connections(self, db: Session, *, user_id: int) -> dict:
        records = data_connection_repository.list_by_user(db, user_id=user_id)
        payload = {
            "shopify": {"connected": False, "status": "DISCONNECTED"},
            "amazon": {"connected": False, "status": "DISCONNECTED"},
            "tiktok": {"connected": False, "status": "DISCONNECTED"},
            "google_ads": {"connected": False, "status": "DISCONNECTED"},
        }
        for record in records:
            normalized_status = self._normalize_status(record.status)
            payload[str(record.platform)] = {
                "connected": normalized_status == "CONNECTED",
                "status": normalized_status,
                "permissions": list(record.permission_scope or []),
                "shop_domain": record.shop_domain,
                "last_sync": record.last_synced_at.isoformat() if record.last_synced_at else None,
            }
        return payload

    def start_shopify_connection(self, *, user_id: int, workspace_id: int, shop_domain: str) -> dict:
        return shopify_oauth_service.generate_authorization_url(user_id=user_id, workspace_id=workspace_id, shop_domain=shop_domain)

    async def complete_shopify_connection(self, db: Session, *, code: str, shop: str, state: str, hmac_value: str | None) -> dict:
        oauth_result = await shopify_oauth_service.handle_callback(code=code, shop=shop, state=state, hmac_value=hmac_value)
        record = data_connection_repository.upsert(
            db,
            user_id=int(oauth_result["user_id"]),
            platform="shopify",
            status="CONNECTED",
            encrypted_access_token=token_encryption.encrypt(str(oauth_result["access_token"])),
            encrypted_refresh_token=token_encryption.encrypt(str(oauth_result.get("refresh_token") or "")),
            expires_at=oauth_result.get("expires_at"),
            permission_scope=list(oauth_result.get("permission_scope") or []),
            shop_domain=str(oauth_result.get("shop_domain") or ""),
            external_account_id=str(oauth_result.get("external_account_id") or ""),
            connection_meta={"connected_via": "oauth"},
            last_synced_at=None,
            last_sync_error=None,
        )
        sync_payload = shopify_sync_service.sync_connection(
            db,
            user_id=int(oauth_result["user_id"]),
            workspace_id=int(oauth_result.get("workspace_id") or 0) or None,
            reason="first_sync",
        )
        return {
            "platform": "shopify",
            "connected": True,
            "status": record.status,
            "shop_domain": record.shop_domain,
            "permissions": list(record.permission_scope or []),
            "last_sync": datetime.now(UTC).isoformat(),
            "sync_summary": sync_payload.get("summary") or {},
        }

    def revoke_connection(self, db: Session, *, user_id: int, platform: str) -> dict:
        record = data_connection_repository.revoke(db, user_id=user_id, platform=platform)
        if not record:
            raise AppError("DATA_CONNECTION_NOT_FOUND", "没有找到这个平台连接", "market_connection", 404)
        return {"platform": platform, "connected": False, "status": "REVOKED", "data_deleted": True}

    def commercial_report(self, db: Session, *, user_id: int, keyword: str, region: str = "US") -> dict:
        from app.services.market_intelligence_engine import market_intelligence_engine

        market_report = market_intelligence_engine.analyze_keyword(db, keyword=keyword, region=region, category=None, user_id=user_id)
        shopify_signal = self._shopify_commercial_signal(db, user_id=user_id, keyword=keyword)
        commercial_score = round(float(shopify_signal.get("commercial_reality_score") or 0), 2)
        market_score = round(float(market_report.get("market_score") or 0), 2)
        combined_confidence = round(
            max(
                0.0,
                min(
                    1.0,
                    float(market_report.get("confidence_score") or market_report.get("confidence") or 0) * 0.6
                    + float(shopify_signal.get("commercial_confidence") or 0) * 0.4,
                ),
            ),
            4,
        )
        recommendation = str(market_report.get("recommendation") or "WATCH")
        if combined_confidence < 0.6:
            recommendation = "WATCH"
        return {
            "keyword": keyword,
            "country": region,
            "market_score": market_score,
            "commercial_score": commercial_score,
            "commercial_reality_score": commercial_score,
            "confidence": combined_confidence,
            "confidence_score": combined_confidence,
            "real_data_ratio": market_report.get("real_data_ratio"),
            "data_sources": {
                "market": market_report.get("source_status") or {},
                "commercial": shopify_signal.get("source_status") or {},
            },
            "recommendation": recommendation,
            "real_sales_signal": shopify_signal.get("real_sales_signal"),
            "customer_validation": shopify_signal.get("customer_validation"),
            "sales_country": shopify_signal.get("sales_country"),
            "product_validation": shopify_signal.get("product_validation"),
            "shopify_commercial_signal": shopify_signal,
        }

    def _shopify_connection(self, db: Session, *, user_id: int):
        record = data_connection_repository.get_by_user_platform(db, user_id=user_id, platform="shopify")
        if not record or self._normalize_status(record.status) != "CONNECTED":
            return None
        return record

    def _shopify_commercial_signal(self, db: Session, *, user_id: int, keyword: str) -> dict:
        record = self._shopify_connection(db, user_id=user_id)
        if not record:
            return {
                "platform": "shopify",
                "connected": False,
                "source_status": {"shopify": "disconnected"},
                "commercial_confidence": 0.0,
                "commercial_reality_score": 0.0,
            }
        access_token = token_encryption.decrypt(record.encrypted_access_token)
        products = self.shopify.fetch_products_with_token(access_token=access_token, shop_domain=record.shop_domain)
        orders = self.shopify.fetch_orders_with_token(access_token=access_token, shop_domain=record.shop_domain)
        if isinstance(products, dict) and products.get("error"):
            return {
                "platform": "shopify",
                "connected": True,
                "source_status": {"shopify": "error"},
                "error": products.get("error"),
                "detail": products.get("detail"),
                "commercial_confidence": 0.0,
                "commercial_reality_score": 0.0,
            }
        if isinstance(orders, dict) and orders.get("error"):
            return {
                "platform": "shopify",
                "connected": True,
                "source_status": {"shopify": "partial"},
                "orders_error": orders.get("detail"),
                "commercial_confidence": 0.2,
                "commercial_reality_score": 0.0,
            }

        filtered_products = [
            item for item in (products or [])
            if str(keyword or "").strip().lower() in str(item.get("title") or "").lower()
        ] if str(keyword or "").strip() else list(products or [])
        sales_volume = 0
        revenue = 0.0
        refunded_order_count = 0
        country_counter: Counter[str] = Counter()
        customer_order_counter: Counter[str] = Counter()
        related_order_count = 0
        for order in orders or []:
            line_items = list(order.get("line_items") or [])
            related = False
            for line in line_items:
                title = str(line.get("title") or "").lower()
                quantity = int(line.get("quantity") or 0)
                if not filtered_products or str(keyword or "").strip().lower() in title:
                    related = True
                    sales_volume += quantity
            if related:
                related_order_count += 1
                revenue += float(order.get("current_total_price") or order.get("total_price") or 0)
                refunds = order.get("refunds") or []
                if refunds:
                    refunded_order_count += 1
                shipping = order.get("shipping_address") or {}
                country = str(shipping.get("country_code") or shipping.get("country") or "unknown")
                country_counter[country] += 1
                customer = order.get("customer") or {}
                customer_id = str(customer.get("id") or "")
                if customer_id:
                    customer_order_counter[customer_id] += 1

        avg_order_value = round(revenue / related_order_count, 2) if related_order_count else 0.0
        repeat_customer_count = sum(1 for _, count in customer_order_counter.items() if count > 1)
        repeat_purchase_rate = round(repeat_customer_count / max(len(customer_order_counter), 1), 4) if customer_order_counter else 0.0
        refund_rate = round(refunded_order_count / max(related_order_count, 1), 4) if related_order_count else 0.0
        product_success_rate = round(related_order_count / max(len(filtered_products) or len(products or []), 1), 4)
        customer_validation = min(100.0, related_order_count * 5)
        real_sales_signal = min(100.0, sales_volume * 2)
        market_fit_score = round(min(100.0, product_success_rate * 100 * 0.5 + customer_validation * 0.5), 2)
        repeat_purchase_signal = round(min(100.0, repeat_purchase_rate * 100), 2)
        profit_validation = round(max(0.0, min(100.0, avg_order_value * (1 - refund_rate) / 2)), 2)
        commercial_reality_score = round(
            min(
                100.0,
                real_sales_signal * 0.3
                + customer_validation * 0.2
                + market_fit_score * 0.2
                + repeat_purchase_signal * 0.15
                + profit_validation * 0.15,
            ),
            2,
        )
        return {
            "platform": "shopify",
            "connected": True,
            "source_status": {"shopify": "CONNECTED"},
            "sales_volume": sales_volume,
            "conversion_rate": None,
            "avg_order_value": avg_order_value,
            "country_distribution": dict(country_counter),
            "sales_country": dict(country_counter),
            "product_success_rate": product_success_rate,
            "product_validation": round(product_success_rate * 100, 2),
            "repeat_purchase_rate": repeat_purchase_rate,
            "refund_rate": refund_rate,
            "real_sales_signal": round(real_sales_signal, 2),
            "customer_validation": round(customer_validation, 2),
            "market_fit_score": market_fit_score,
            "repeat_purchase_signal": repeat_purchase_signal,
            "profit_validation": profit_validation,
            "commercial_reality_score": commercial_reality_score,
            "commercial_confidence": 0.92 if related_order_count > 0 else 0.6,
            "matched_product_count": len(filtered_products),
            "matched_order_count": related_order_count,
        }


commercial_data_connection_engine = CommercialDataConnectionEngine()
