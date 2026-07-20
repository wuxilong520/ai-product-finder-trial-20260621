from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.runtime import AppError
from app.core.security import create_access_token, decode_access_token


class ShopifyOAuthService:
    def generate_authorization_url(self, *, user_id: int, workspace_id: int, shop_domain: str) -> dict:
        normalized_domain = self._normalize_shop_domain(shop_domain)
        if not str(settings.shopify_client_id or "").strip() or not str(settings.shopify_client_secret or "").strip():
            raise AppError("SHOPIFY_OAUTH_NOT_CONFIGURED", "缺少 Shopify OAuth 配置", "oauth", 500)
        if not str(settings.shopify_app_url or "").strip():
            raise AppError("SHOPIFY_APP_URL_MISSING", "缺少 SHOPIFY_APP_URL", "oauth", 500)
        redirect_uri = str(settings.shopify_oauth_redirect_uri or "").strip()
        if not redirect_uri:
            raise AppError("SHOPIFY_OAUTH_REDIRECT_MISSING", "缺少 SHOPIFY_OAUTH_REDIRECT_URI", "oauth", 500)
        state = create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=30),
            extra_payload={"workspace_id": workspace_id, "platform": "shopify", "shop_domain": normalized_domain, "purpose": "market_connect"},
        )
        query = urlencode(
            {
                "client_id": str(settings.shopify_client_id or "").strip(),
                "scope": str(settings.shopify_oauth_scopes or "read_products,read_orders"),
                "redirect_uri": redirect_uri,
                "state": state,
            }
        )
        return {
            "platform": "shopify",
            "shop_domain": normalized_domain,
            "authorize_url": f"https://{normalized_domain}/admin/oauth/authorize?{query}",
            "state": state,
            "scopes": str(settings.shopify_oauth_scopes or "read_products,read_orders").split(","),
        }

    async def handle_callback(self, *, code: str, shop: str, state: str, hmac_value: str | None) -> dict:
        normalized_domain = self._normalize_shop_domain(shop)
        payload = decode_access_token(state)
        if payload.get("platform") != "shopify":
            raise AppError("SHOPIFY_OAUTH_STATE_INVALID", "Shopify state 无效", "oauth", 400)
        if payload.get("shop_domain") != normalized_domain:
            raise AppError("SHOPIFY_OAUTH_SHOP_MISMATCH", "Shopify 店铺域名不匹配", "oauth", 400)
        if hmac_value and not self._verify_hmac(code=code, shop=normalized_domain, state=state, hmac_value=hmac_value):
            raise AppError("SHOPIFY_OAUTH_HMAC_INVALID", "Shopify OAuth HMAC 校验失败", "oauth", 400)

        return await self.exchange_code_for_token(code=code, shop=normalized_domain, payload=payload)

    async def exchange_code_for_token(self, *, code: str, shop: str, payload: dict) -> dict:
        redirect_uri = str(settings.shopify_oauth_redirect_uri or "").strip()
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"https://{shop}/admin/oauth/access_token",
                json={
                    "client_id": str(settings.shopify_client_id or "").strip(),
                    "client_secret": str(settings.shopify_client_secret or "").strip(),
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
        response.raise_for_status()
        data = response.json() or {}
        access_token = str(data.get("access_token") or "").strip()
        scopes = str(data.get("scope") or "").split(",") if str(data.get("scope") or "").strip() else []
        if not access_token:
            raise AppError("SHOPIFY_OAUTH_TOKEN_MISSING", "Shopify 没有返回 access token", "oauth", 502)
        return {
            "user_id": int(payload.get("sub")),
            "workspace_id": int(payload.get("workspace_id") or 0),
            "shop_domain": shop,
            "access_token": access_token,
            "refresh_token": "",
            "expires_at": None,
            "permission_scope": [item.strip() for item in scopes if item.strip()],
            "external_account_id": shop,
        }

    async def refresh_token(self, *, refresh_token: str, shop_domain: str) -> dict:
        del shop_domain
        if not str(refresh_token or "").strip():
            return {"supported": False, "status": "not_supported", "reason": "Shopify 当前这套 OAuth token 没有 refresh token"}
        return {"supported": False, "status": "not_supported", "reason": "Shopify 当前这套 OAuth token 没有 refresh token"}

    def build_authorize_url(self, *, user_id: int, workspace_id: int, shop_domain: str) -> dict:
        return self.generate_authorization_url(user_id=user_id, workspace_id=workspace_id, shop_domain=shop_domain)

    async def exchange_code(self, *, code: str, shop: str, state: str, hmac_value: str | None) -> dict:
        return await self.handle_callback(code=code, shop=shop, state=state, hmac_value=hmac_value)

    def _normalize_shop_domain(self, shop_domain: str) -> str:
        text = str(shop_domain or "").strip().lower()
        if not text:
            raise AppError("SHOPIFY_SHOP_DOMAIN_REQUIRED", "缺少 shop_domain", "oauth", 400)
        return text.removeprefix("https://").removeprefix("http://").strip("/").split("/")[0]

    def _verify_hmac(self, *, code: str, shop: str, state: str, hmac_value: str) -> bool:
        message = urlencode({"code": code, "shop": shop, "state": state})
        digest = hmac.new(
            str(settings.shopify_client_secret or "").encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(digest, str(hmac_value or ""))


shopify_oauth_service = ShopifyOAuthService()
