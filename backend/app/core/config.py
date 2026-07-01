import os
from pathlib import Path

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
    alipay_app_id: str = os.getenv("ALIPAY_APP_ID", "")
    alipay_private_key: str = os.getenv("ALIPAY_PRIVATE_KEY", "")
    alipay_public_key: str = os.getenv("ALIPAY_PUBLIC_KEY", "")
    alipay_notify_url: str = os.getenv("ALIPAY_NOTIFY_URL", "")
    alipay_return_url: str = os.getenv("ALIPAY_RETURN_URL", "")
    alipay_gateway_url: str = os.getenv("ALIPAY_GATEWAY_URL", "https://openapi.alipay.com/gateway.do")
    wechat_pay_app_id: str = os.getenv("WECHAT_PAY_APP_ID", "")
    wechat_pay_mch_id: str = os.getenv("WECHAT_PAY_MCH_ID", "")
    wechat_pay_api_v3_key: str = os.getenv("WECHAT_PAY_API_V3_KEY", "")
    wechat_pay_cert_serial: str = os.getenv("WECHAT_PAY_CERT_SERIAL", "")
    wechat_pay_private_key: str = os.getenv("WECHAT_PAY_PRIVATE_KEY", "")
    wechat_pay_notify_url: str = os.getenv("WECHAT_PAY_NOTIFY_URL", "")

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


settings = Settings()
