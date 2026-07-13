from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "商航AI"
    app_env: str = os.getenv("APP_ENV", "development")
    app_debug: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    api_v1_prefix: str = "/api/v1"

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./product_mvp.db")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")
    mock_ai_enabled: bool = False
    mock_crawler_enabled: bool = False

    secret_key: str = os.getenv("SECRET_KEY", "change_me_to_a_secure_secret")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", os.getenv("FRONTEND_URL", ""))
    backend_url: str = os.getenv("BACKEND_URL", "")
    frontend_url: str = os.getenv("FRONTEND_URL", "")
    ws_url: str = os.getenv("WS_URL", "")
    next_public_api_base_url: str = os.getenv("NEXT_PUBLIC_API_BASE_URL", "")
    next_public_ws_url: str = os.getenv("NEXT_PUBLIC_WS_URL", "")
    first_superuser_email: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    first_superuser_password: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "change_this_password")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "465"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "true").lower() == "true"
    auth_code_expire_minutes: int = int(os.getenv("AUTH_CODE_EXPIRE_MINUTES", "10"))
    auth_challenge_expire_minutes: int = int(os.getenv("AUTH_CHALLENGE_EXPIRE_MINUTES", "10"))
    auth_challenge_rate: float = float(os.getenv("AUTH_CHALLENGE_RATE", "0.15"))
    auth_challenge_fail_threshold: int = int(os.getenv("AUTH_CHALLENGE_FAIL_THRESHOLD", "2"))
    wechat_pay_app_id: str = os.getenv("WECHAT_PAY_APP_ID", "")
    wechat_pay_mch_id: str = os.getenv("WECHAT_PAY_MCH_ID", "")
    wechat_pay_api_v3_key: str = os.getenv("WECHAT_PAY_API_V3_KEY", "")
    wechat_pay_cert_serial: str = os.getenv("WECHAT_PAY_CERT_SERIAL", "")
    wechat_pay_private_key: str = os.getenv("WECHAT_PAY_PRIVATE_KEY", "")
    wechat_pay_notify_url: str = os.getenv("WECHAT_PAY_NOTIFY_URL", "")
    shopify_store_base_url: str = os.getenv("SHOPIFY_STORE_BASE_URL", "")
    shopify_client_id: str = os.getenv("SHOPIFY_CLIENT_ID", os.getenv("SHOPIFY_API_KEY", ""))
    shopify_client_secret: str = os.getenv("SHOPIFY_CLIENT_SECRET", os.getenv("SHOPIFY_API_SECRET", ""))
    shopify_app_url: str = os.getenv("SHOPIFY_APP_URL", "")
    shopify_admin_access_token: str = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN", "")
    shopify_oauth_redirect_uri: str = os.getenv("SHOPIFY_OAUTH_REDIRECT_URI", "")
    shopify_oauth_scopes: str = os.getenv("SHOPIFY_OAUTH_SCOPES", "read_products,read_orders")
    shopify_execution_mode: str = os.getenv("SHOPIFY_EXECUTION_MODE", "mock")
    dataforseo_login: str = os.getenv("DATAFORSEO_LOGIN", "")
    dataforseo_password: str = os.getenv("DATAFORSEO_PASSWORD", "")
    dataforseo_base_url: str = os.getenv("DATAFORSEO_BASE_URL", "https://api.dataforseo.com")
    bing_webmaster_api_key: str = os.getenv("BING_WEBMASTER_API_KEY", "")
    google_ads_developer_token: str = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    google_ads_client_id: str = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
    google_ads_client_secret: str = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")
    google_ads_refresh_token: str = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")
    google_ads_customer_id: str = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "")
    google_ads_login_customer_id: str = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
    amazon_paapi_access_key: str = os.getenv("AMAZON_PAAPI_ACCESS_KEY", "")
    amazon_paapi_secret_key: str = os.getenv("AMAZON_PAAPI_SECRET_KEY", "")
    amazon_paapi_partner_tag: str = os.getenv("AMAZON_PAAPI_PARTNER_TAG", "")
    amazon_paapi_region: str = os.getenv("AMAZON_PAAPI_REGION", "")
    amazon_paapi_host: str = os.getenv("AMAZON_PAAPI_HOST", "")
    tiktok_marketing_access_token: str = os.getenv("TIKTOK_MARKETING_ACCESS_TOKEN", "")
    tiktok_advertiser_id: str = os.getenv("TIKTOK_ADVERTISER_ID", "")
    tiktok_app_id: str = os.getenv("TIKTOK_APP_ID", "")
    tiktok_app_secret: str = os.getenv("TIKTOK_APP_SECRET", "")
    meta_access_token: str = os.getenv("META_ACCESS_TOKEN", "")
    pinterest_access_token: str = os.getenv("PINTEREST_ACCESS_TOKEN", "")
    amazon_oauth_client_id: str = os.getenv("AMAZON_OAUTH_CLIENT_ID", "")
    amazon_oauth_client_secret: str = os.getenv("AMAZON_OAUTH_CLIENT_SECRET", "")
    amazon_oauth_redirect_uri: str = os.getenv("AMAZON_OAUTH_REDIRECT_URI", "")
    google_oauth_redirect_uri: str = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "")
    tiktok_oauth_redirect_uri: str = os.getenv("TIKTOK_OAUTH_REDIRECT_URI", "")
    token_encryption_key: str = os.getenv("TOKEN_ENCRYPTION_KEY", "")

    model_config = SettingsConfigDict(
        env_file=(str(PROJECT_ROOT / ".env"), str(BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    def required_backend_env(self) -> list[str]:
        return [
            "BACKEND_URL",
            "FRONTEND_URL",
            "FRONTEND_ORIGIN",
            "WS_URL",
            "NEXT_PUBLIC_API_BASE_URL",
            "NEXT_PUBLIC_WS_URL",
        ]

    def missing_backend_env(self) -> list[str]:
        env_map = {
            "BACKEND_URL": self.backend_url,
            "FRONTEND_URL": self.frontend_url,
            "FRONTEND_ORIGIN": self.frontend_origin,
            "WS_URL": self.ws_url,
            "NEXT_PUBLIC_API_BASE_URL": self.next_public_api_base_url,
            "NEXT_PUBLIC_WS_URL": self.next_public_ws_url,
        }
        return [key for key, value in env_map.items() if not str(value or "").strip()]

    def cors_origins(self) -> list[str]:
        raw_value = str(self.frontend_origin or "").strip()
        if not raw_value:
            return []
        return [item.strip().rstrip("/") for item in raw_value.split(",") if item.strip()]

    def has_local_address(self, value: str | None) -> bool:
        text = str(value or "").strip().lower()
        if not text:
            return False
        host = urlparse(text).hostname or text
        return host in {"127.0.0.1", "localhost", "0.0.0.0"}


settings = Settings()
