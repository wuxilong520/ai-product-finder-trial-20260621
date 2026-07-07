from __future__ import annotations

import base64
import json
import time
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from app.adapters.platform.base_platform import PlatformAdapter
from app.core.config import settings
from app.core.runtime import log_info


class ShopifyPlatformAdapter(PlatformAdapter):
    adapter_name = "shopify_admin_api"
    api_version = "2024-10"

    def __init__(self) -> None:
        self._access_token: str | None = None
        self._access_token_expires_at: float = 0

    def _normalized_base_url(self) -> str:
        return str(settings.shopify_store_base_url or "").strip().rstrip("/")

    def _api_credentials_ready(self) -> bool:
        return bool(
            self._normalized_base_url()
            and str(settings.shopify_api_key or "").strip()
            and str(settings.shopify_api_secret or "").strip()
        )

    def _error_state(self, error_code: str, detail: str) -> dict:
        payload = {
            "error": error_code,
            "detail": detail,
            "is_real": False,
            "is_real_data": False,
            "raw_platform": "shopify",
            "data_source_type": "error",
        }
        log_info(
            "SHOPIFY_API_ERROR | "
            + json.dumps(payload, ensure_ascii=False)
        )
        return payload

    def _build_endpoint(self, path: str) -> str:
        return f"{self._normalized_base_url()}/admin/api/{self.api_version}/{path.lstrip('/')}"

    def _build_token_endpoint(self) -> str:
        return f"{self._normalized_base_url()}/admin/oauth/access_token"

    def _build_client_credentials_payload(self) -> bytes:
        return (
            f"grant_type=client_credentials&"
            f"client_id={quote(str(settings.shopify_api_key or '').strip())}&"
            f"client_secret={quote(str(settings.shopify_api_secret or '').strip())}"
        ).encode("utf-8")

    def _access_token_alive(self) -> bool:
        return bool(self._access_token and time.time() < (self._access_token_expires_at - 60))

    def _request_access_token(self) -> tuple[str, int]:
        if not self._api_credentials_ready():
            raise ValueError("SHOPIFY_API_NOT_CONFIGURED")

        request = Request(
            self._build_token_endpoint(),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "ShangHangAI/1.0",
            },
            data=self._build_client_credentials_payload(),
            method="POST",
        )

        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))

        access_token = str(payload.get("access_token") or "").strip()
        expires_in = int(payload.get("expires_in") or 0)
        if not access_token:
            raise ValueError("SHOPIFY_TOKEN_MISSING")
        return access_token, expires_in

    def _get_access_token(self) -> str:
        if self._access_token_alive():
            return str(self._access_token)

        access_token, expires_in = self._request_access_token()
        self._access_token = access_token
        self._access_token_expires_at = time.time() + expires_in
        return access_token

    def _request_json(self, endpoint: str) -> dict:
        if not self._api_credentials_ready():
            raise ValueError("SHOPIFY_API_NOT_CONFIGURED")

        request = Request(
            endpoint,
            headers={
                "X-Shopify-Access-Token": self._get_access_token(),
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "ShangHangAI/1.0",
            },
            method="GET",
        )
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8", errors="ignore"))

    def _normalize_product(self, product: dict) -> dict:
        variants = product.get("variants") or []
        first_variant = variants[0] if variants else {}
        inventory_quantity = int(first_variant.get("inventory_quantity") or 0)
        return {
            "id": str(product.get("id") or ""),
            "title": str(product.get("title") or ""),
            "price": str(first_variant.get("price") or ""),
            "inventory_quantity": inventory_quantity,
            "currency": "USD",
            "is_real_data": True,
            "is_real_platform_data": True,
            "data_source_type": "real",
            "raw_platform": "shopify",
            "product_id": str(product.get("id") or ""),
            "supplier": str(product.get("vendor") or "Shopify"),
            "availability": inventory_quantity > 0,
            "shipping_time": "shopify_admin_sync",
        }

    def _fetch_products(self) -> list[dict] | dict:
        if not self._api_credentials_ready():
            return self._error_state(
                "SHOPIFY_API_NOT_CONFIGURED",
                "缺少 SHOPIFY_STORE_BASE_URL / SHOPIFY_API_KEY / SHOPIFY_API_SECRET",
            )

        endpoint = self._build_endpoint("products.json")
        try:
            payload = self._request_json(endpoint)
            products = payload.get("products")
            if not isinstance(products, list):
                return self._error_state(
                    "SHOPIFY_API_INVALID_RESPONSE",
                    "Shopify products.json 返回结构不符合预期",
                )
            normalized = [self._normalize_product(item) for item in products]
            log_info(
                "SHOPIFY_API_OK | "
                + json.dumps(
                    {
                        "endpoint": endpoint,
                        "product_count": len(normalized),
                        "is_real_data": True,
                    },
                    ensure_ascii=False,
                )
            )
            return normalized
        except HTTPError as exc:
            detail = f"HTTP {exc.code}"
            try:
                body = exc.read().decode("utf-8", errors="ignore")
                if body:
                    detail = f"{detail} | {body}"
            except Exception:
                pass
            return self._error_state(
                "SHOPIFY_API_HTTP_ERROR",
                detail,
            )
        except URLError as exc:
            return self._error_state(
                "SHOPIFY_API_UNREACHABLE",
                str(exc.reason),
            )
        except ValueError as exc:
            if str(exc) == "SHOPIFY_API_NOT_CONFIGURED":
                return self._error_state(
                    "SHOPIFY_API_NOT_CONFIGURED",
                    "缺少 Shopify API 配置",
                )
            return self._error_state("SHOPIFY_API_VALUE_ERROR", str(exc))
        except Exception as exc:
            return self._error_state(
                "SHOPIFY_API_UNKNOWN_ERROR",
                str(exc),
            )

    def search_product(self, keyword: str):
        products = self._fetch_products()
        if isinstance(products, dict):
            return [products]
        keyword_lower = str(keyword or "").strip().lower()
        if not keyword_lower:
            return products
        return [
            item for item in products
            if keyword_lower in str(item.get("title") or "").lower()
        ]

    def get_price(self, product_id: str):
        products = self._fetch_products()
        if isinstance(products, dict):
            return products
        for item in products:
            if str(item.get("id")) == str(product_id):
                return item
        return self._error_state(
            "SHOPIFY_PRODUCT_NOT_FOUND",
            f"没有找到 product_id={product_id} 的商品",
        )

    def publish_product(self, product: dict):
        return self._error_state(
            "SHOPIFY_PUBLISH_NOT_IMPLEMENTED",
            "当前 Shopify 平台适配器只完成真实读取，未开放真实发布。",
        )

    def get_inventory(self, product_id: str):
        product = self.get_price(product_id)
        if product.get("error"):
            return product
        return {
            "id": product.get("id", ""),
            "title": product.get("title", ""),
            "inventory_quantity": int(product.get("inventory_quantity") or 0),
            "currency": product.get("currency", "USD"),
            "is_real_data": True,
            "is_real_platform_data": True,
            "data_source_type": "real",
            "raw_platform": "shopify",
        }

    def oauth_blueprint(self, shop_domain: str) -> dict:
        return {
            "channel": "shopify",
            "shop_domain": shop_domain,
            "oauth_status": "reserved",
        }

    def update_product(self, product_id: str, product: dict):
        return self._error_state(
            "SHOPIFY_UPDATE_NOT_IMPLEMENTED",
            f"当前未开放真实 update_product，product_id={product_id}",
        )

    def pull_real_products(self, keyword: str) -> list[dict] | dict:
        return self.search_product(keyword)

    def sync_price(self, product_id: str) -> dict:
        return self.get_price(product_id)

    def sync_inventory(self, product_id: str) -> dict:
        return self.get_inventory(product_id)
