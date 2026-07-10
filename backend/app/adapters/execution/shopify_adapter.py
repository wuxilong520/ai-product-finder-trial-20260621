from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.adapters.execution.base import ExecutionAdapterBase
from app.core.config import settings
from app.core.contracts import ListingDraft, OAuthSession, PublishReceipt
from app.core.runtime import log_info


class ShopifyExecutionAdapter(ExecutionAdapterBase):
    adapter_name = "shopify_admin_execution"
    supported_channels = ("shopify",)

    def _get_mode(self) -> str:
        return (os.getenv("SHOPIFY_EXECUTION_MODE") or "mock").strip().lower()

    def _shop_domain(self, shop_domain: str) -> str:
        raw_domain = str(shop_domain or "").strip()
        if raw_domain:
            return raw_domain.replace("https://", "").replace("http://", "").strip("/ ")
        base_url = str(settings.shopify_store_base_url or "").strip()
        return (
            base_url.replace("https://", "")
            .replace("http://", "")
            .replace("/admin", "")
            .strip("/ ")
        )

    def _build_admin_api_url(self, *, shop_domain: str, path: str) -> str:
        return f"https://{self._shop_domain(shop_domain)}/admin/api/2024-10/{path.lstrip('/')}"

    def _admin_token(self, access_token: str | None = None) -> str:
        token = str(access_token or settings.shopify_admin_access_token or "").strip()
        if token:
            return token
        api_secret = str(settings.shopify_api_secret or "").strip()
        if api_secret:
            return api_secret
        raise ValueError("SHOPIFY_ADMIN_TOKEN_MISSING")

    def _headers(self, *, access_token: str | None = None) -> dict[str, str]:
        return {
            "X-Shopify-Access-Token": self._admin_token(access_token),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ShangHangAI/1.0",
        }

    def _build_product_payload(
        self,
        *,
        listing: ListingDraft,
        draft_mode: bool,
        extra_metafields: dict | None = None,
    ) -> dict:
        metafields = [
            {
                "namespace": "shanghang_ai",
                "key": "selling_points",
                "type": "multi_line_text_field",
                "value": "\n".join(listing.selling_points),
            }
        ]
        for key, value in (extra_metafields or {}).items():
            metafields.append(
                {
                    "namespace": "shanghang_ai",
                    "key": str(key),
                    "type": "single_line_text_field",
                    "value": str(value),
                }
            )
        return {
            "product": {
                "title": listing.listing_title,
                "body_html": listing.listing_description,
                "tags": ", ".join(listing.tags),
                "status": "draft" if draft_mode else "active",
                "variants": [
                    {
                        "price": str(listing.suggested_price),
                    }
                ],
                "metafields": metafields,
            }
        }

    def _request_json(
        self,
        *,
        method: str,
        endpoint: str,
        payload: dict | None = None,
        access_token: str | None = None,
    ) -> dict:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            endpoint,
            headers=self._headers(access_token=access_token),
            data=data,
            method=method,
        )
        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="ignore")
        return json.loads(body) if body else {}

    def _error_state(self, error_code: str, detail: str, *, endpoint: str = "") -> dict:
        payload = {
            "status": "failed",
            "error": error_code,
            "detail": detail,
            "endpoint": endpoint,
            "is_real": False,
        }
        log_info(f"SHOPIFY_EXECUTION_ERROR | {json.dumps(payload, ensure_ascii=False)}")
        return payload

    def build_oauth_session(self, *, shop_domain: str) -> OAuthSession:
        normalized_domain = self._shop_domain(shop_domain)
        state = f"oauth-state-{normalized_domain.replace('.', '-')}"
        client_id = os.getenv("SHOPIFY_CLIENT_ID", "shopify_client_missing")
        redirect_uri = os.getenv("SHOPIFY_REDIRECT_URI", "https://shanghang-ai.local/shopify/callback")
        return OAuthSession(
            channel="shopify",
            shop_domain=normalized_domain,
            authorize_url=(
                f"https://{normalized_domain}/admin/oauth/authorize"
                f"?client_id={client_id}"
                f"&scope=write_products,read_products"
                f"&redirect_uri={redirect_uri}"
                f"&state={state}"
            ),
            state=state,
            connected=False,
        )

    def exchange_oauth_code(self, *, shop_domain: str, code: str) -> OAuthSession:
        normalized_domain = self._shop_domain(shop_domain)
        return OAuthSession(
            channel="shopify",
            shop_domain=normalized_domain,
            authorize_url=f"https://{normalized_domain}/admin/oauth/authorize",
            state=f"oauth-state-{normalized_domain.replace('.', '-')}",
            connected=True,
            access_token=code,
        )

    def create_product(
        self,
        *,
        shop_domain: str,
        listing: ListingDraft,
        access_token: str | None = None,
        draft_mode: bool = False,
        extra_metafields: dict | None = None,
    ) -> dict:
        endpoint = self._build_admin_api_url(shop_domain=shop_domain, path="products.json")
        mode = self._get_mode()
        if mode != "real":
            return self._error_state(
                "SHOPIFY_EXECUTION_NOT_REAL_MODE",
                "当前执行模式不是 real，已禁止用 mock 冒充创建草稿",
                endpoint=endpoint,
            )
        try:
            payload = self._build_product_payload(
                listing=listing,
                draft_mode=draft_mode,
                extra_metafields=extra_metafields,
            )
            response = self._request_json(
                method="POST",
                endpoint=endpoint,
                payload=payload,
                access_token=access_token,
            )
            product = dict(response.get("product") or {})
            product_id = str(product.get("id") or "")
            if not product_id:
                return self._error_state(
                    "SHOPIFY_DRAFT_CREATE_FAILED",
                    "Shopify 返回里没有 product id",
                    endpoint=endpoint,
                )
            result = {
                "status": "draft_created" if draft_mode else "published",
                "product_id": product_id,
                "handle": str(product.get("handle") or ""),
                "admin_graphql_api_id": str(product.get("admin_graphql_api_id") or ""),
                "mode": "real",
                "is_real": True,
                "endpoint": endpoint,
            }
            log_info(f"SHOPIFY_EXECUTION_OK | {json.dumps(result, ensure_ascii=False)}")
            return result
        except ValueError as exc:
            return self._error_state(str(exc), "缺少 Shopify Draft 所需管理员访问令牌", endpoint=endpoint)
        except HTTPError as exc:
            detail = f"HTTP {exc.code}"
            try:
                body = exc.read().decode("utf-8", errors="ignore")
                if body:
                    detail = f"{detail} | {body}"
            except Exception:
                pass
            return self._error_state("SHOPIFY_HTTP_ERROR", detail, endpoint=endpoint)
        except URLError as exc:
            return self._error_state("SHOPIFY_UNREACHABLE", str(exc.reason), endpoint=endpoint)
        except Exception as exc:
            return self._error_state("SHOPIFY_CREATE_UNKNOWN_ERROR", str(exc), endpoint=endpoint)

    def update_product(
        self,
        *,
        shop_domain: str,
        product_id: str,
        listing: ListingDraft,
        access_token: str | None = None,
    ) -> dict:
        endpoint = self._build_admin_api_url(shop_domain=shop_domain, path=f"products/{product_id}.json")
        if self._get_mode() != "real":
            return self._error_state(
                "SHOPIFY_EXECUTION_NOT_REAL_MODE",
                "当前执行模式不是 real，已禁止 mock 更新商品",
                endpoint=endpoint,
            )
        try:
            payload = self._build_product_payload(listing=listing, draft_mode=False)
            payload["product"]["id"] = product_id
            response = self._request_json(
                method="PUT",
                endpoint=endpoint,
                payload=payload,
                access_token=access_token,
            )
            product = dict(response.get("product") or {})
            return {
                "status": "updated",
                "product_id": str(product.get("id") or product_id),
                "mode": "real",
                "is_real": True,
                "endpoint": endpoint,
            }
        except Exception as exc:
            return self._error_state("SHOPIFY_UPDATE_FAILED", str(exc), endpoint=endpoint)

    def fetch_product(self, *, shop_domain: str, product_id: str, access_token: str | None = None) -> dict:
        endpoint = self._build_admin_api_url(shop_domain=shop_domain, path=f"products/{product_id}.json")
        if self._get_mode() != "real":
            return self._error_state(
                "SHOPIFY_EXECUTION_NOT_REAL_MODE",
                "当前执行模式不是 real，已禁止 mock 查询商品",
                endpoint=endpoint,
            )
        try:
            response = self._request_json(
                method="GET",
                endpoint=endpoint,
                access_token=access_token,
            )
            return {
                "status": "fetched",
                "mode": "real",
                "is_real": True,
                "endpoint": endpoint,
                "product": dict(response.get("product") or {}),
            }
        except Exception as exc:
            return self._error_state("SHOPIFY_FETCH_FAILED", str(exc), endpoint=endpoint)

    def fetch_orders(
        self,
        *,
        shop_domain: str | None = None,
        access_token: str | None = None,
        limit: int = 20,
    ) -> dict:
        endpoint = self._build_admin_api_url(
            shop_domain=shop_domain or "",
            path=f"orders.json?status=any&limit={max(1, min(limit, 250))}",
        )
        if self._get_mode() != "real":
            return self._error_state(
                "SHOPIFY_EXECUTION_NOT_REAL_MODE",
                "当前执行模式不是 real，已禁止 mock 订单反馈",
                endpoint=endpoint,
            )
        try:
            response = self._request_json(
                method="GET",
                endpoint=endpoint,
                access_token=access_token,
            )
            orders = []
            for item in list(response.get("orders") or []):
                refund_total = 0.0
                for refund in list(item.get("refunds") or []):
                    for refund_line in list(refund.get("refund_line_items") or []):
                        refund_total += float(
                            (((refund_line.get("subtotal_set") or {}).get("shop_money") or {}).get("amount")) or 0
                        )
                orders.append(
                    {
                        "id": str(item.get("id") or ""),
                        "name": str(item.get("name") or ""),
                        "financial_status": str(item.get("financial_status") or ""),
                        "total_price": float(item.get("total_price") or 0),
                        "refund_total": round(refund_total, 2),
                        "created_at": str(item.get("created_at") or ""),
                    }
                )
            return {
                "status": "ok",
                "is_real": True,
                "orders": orders,
                "endpoint": endpoint,
            }
        except Exception as exc:
            return self._error_state("SHOPIFY_ORDERS_FAILED", str(exc), endpoint=endpoint)

    def publish_listing(self, *, shop_domain: str, listing: ListingDraft) -> PublishReceipt:
        created = self.create_product(shop_domain=shop_domain, listing=listing, draft_mode=False)
        listing_id = str(created.get("product_id") or "")
        return PublishReceipt(
            channel="shopify",
            status=str(created.get("status") or "failed"),
            listing_id=listing_id,
            publish_url=f"https://{shop_domain}/products/{listing_id}",
            message="Shopify 发布已走执行适配器，是否成功请看 status 与 error 字段。",
        )
