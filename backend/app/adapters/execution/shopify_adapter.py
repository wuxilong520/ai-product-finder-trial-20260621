from __future__ import annotations

import os

from app.adapters.execution.base import ExecutionAdapterBase
from app.core.contracts import ListingDraft, OAuthSession, PublishReceipt
from app.integration.base_client import BaseClient


class ShopifyExecutionAdapter(ExecutionAdapterBase):
    adapter_name = "shopify_mock"
    supported_channels = ("shopify",)

    def _get_mode(self) -> str:
        return (os.getenv("SHOPIFY_EXECUTION_MODE") or "mock").strip().lower()

    def _build_admin_api_url(self, *, shop_domain: str, path: str) -> str:
        return f"https://{shop_domain}/admin/api/2024-01/{path.lstrip('/')}"

    def _build_product_payload(self, *, listing: ListingDraft) -> dict:
        return {
            "product": {
                "title": listing.listing_title,
                "body_html": listing.listing_description,
                "tags": ", ".join(listing.tags),
                "variants": [
                    {
                        "price": str(listing.suggested_price),
                    }
                ],
                "metafields": [
                    {
                        "namespace": "shanghang_ai",
                        "key": "selling_points",
                        "type": "multi_line_text_field",
                        "value": "\n".join(listing.selling_points),
                    }
                ],
            }
        }

    def build_oauth_session(self, *, shop_domain: str) -> OAuthSession:
        state = f"mock-state-{shop_domain.replace('.', '-')}"
        client_id = os.getenv("SHOPIFY_CLIENT_ID", "mock_client")
        redirect_uri = os.getenv("SHOPIFY_REDIRECT_URI", "https://shanghang-ai.local/shopify/callback")
        return OAuthSession(
            channel="shopify",
            shop_domain=shop_domain,
            authorize_url=(
                f"https://{shop_domain}/admin/oauth/authorize"
                f"?client_id={client_id}"
                f"&scope=write_products,read_products"
                f"&redirect_uri={redirect_uri}"
                f"&state={state}"
            ),
            state=state,
            connected=False,
        )

    def exchange_oauth_code(self, *, shop_domain: str, code: str) -> OAuthSession:
        mode = self._get_mode()
        return OAuthSession(
            channel="shopify",
            shop_domain=shop_domain,
            authorize_url=f"https://{shop_domain}/admin/oauth/authorize",
            state=f"mock-state-{shop_domain.replace('.', '-')}",
            connected=True,
            access_token=f"{mode}-token-{code[-6:]}",
        )

    def create_product(self, *, shop_domain: str, listing: ListingDraft, access_token: str | None = None) -> dict:
        mode = self._get_mode()
        client = BaseClient(mode=mode)
        return client.execute(
            mock_handler=lambda: {
                "mode": "mock",
                "method": "POST",
                "endpoint": self._build_admin_api_url(shop_domain=shop_domain, path="products.json"),
                "access_token": access_token,
                "payload": self._build_product_payload(listing=listing),
                "status": "mock_created",
                "product_id": f"shopify-{shop_domain.replace('.', '-')}-001",
            },
            real_handler=lambda: {
                "mode": "real",
                "method": "POST",
                "endpoint": self._build_admin_api_url(shop_domain=shop_domain, path="products.json"),
                "access_token": access_token,
                "payload": self._build_product_payload(listing=listing),
                "status": "real_mode_ready",
                "product_id": f"shopify-{shop_domain.replace('.', '-')}-001",
            },
        )

    def update_product(self, *, shop_domain: str, product_id: str, listing: ListingDraft, access_token: str | None = None) -> dict:
        mode = self._get_mode()
        client = BaseClient(mode=mode)
        return client.execute(
            mock_handler=lambda: {
                "mode": "mock",
                "method": "PUT",
                "endpoint": self._build_admin_api_url(shop_domain=shop_domain, path=f"products/{product_id}.json"),
                "access_token": access_token,
                "payload": self._build_product_payload(listing=listing),
                "status": "mock_updated",
                "product_id": product_id,
            },
            real_handler=lambda: {
                "mode": "real",
                "method": "PUT",
                "endpoint": self._build_admin_api_url(shop_domain=shop_domain, path=f"products/{product_id}.json"),
                "access_token": access_token,
                "payload": self._build_product_payload(listing=listing),
                "status": "real_mode_ready",
                "product_id": product_id,
            },
        )

    def fetch_product(self, *, shop_domain: str, product_id: str, access_token: str | None = None) -> dict:
        mode = self._get_mode()
        client = BaseClient(mode=mode)
        return client.execute(
            mock_handler=lambda: {
                "mode": "mock",
                "method": "GET",
                "endpoint": self._build_admin_api_url(shop_domain=shop_domain, path=f"products/{product_id}.json"),
                "access_token": access_token,
                "status": "mock_fetched",
                "product": {
                    "id": product_id,
                    "handle": product_id,
                    "admin_graphql_api_id": f"gid://shopify/Product/{product_id}",
                },
            },
            real_handler=lambda: {
                "mode": "real",
                "method": "GET",
                "endpoint": self._build_admin_api_url(shop_domain=shop_domain, path=f"products/{product_id}.json"),
                "access_token": access_token,
                "status": "real_mode_ready",
                "product": {
                    "id": product_id,
                    "handle": product_id,
                    "admin_graphql_api_id": f"gid://shopify/Product/{product_id}",
                },
            },
        )

    def publish_listing(self, *, shop_domain: str, listing: ListingDraft) -> PublishReceipt:
        created = self.create_product(shop_domain=shop_domain, listing=listing)
        listing_id = created["product_id"]
        return PublishReceipt(
            channel="shopify",
            status=str(created["status"]),
            listing_id=listing_id,
            publish_url=f"https://{shop_domain}/products/{listing_id}",
            message=f"Shopify {created['mode']} 发布流程已走通，当前阶段保留接口结构。",
        )
