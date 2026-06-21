from pathlib import Path
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "Cross Border Product MVP"
    app_env: str = os.getenv("APP_ENV", "development")
    app_debug: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    api_v1_prefix: str = "/api/v1"

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./product_mvp.db")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    mock_ai_enabled: bool = False
    mock_crawler_enabled: bool = False

    secret_key: str = os.getenv("SECRET_KEY", "change_me_to_a_secure_secret")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", os.getenv("FRONTEND_URL", ""))
    backend_url: str = os.getenv("BACKEND_URL", "")
    frontend_url: str = os.getenv("FRONTEND_URL", "")
    first_superuser_email: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    first_superuser_password: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "change_this_password")

    model_config = SettingsConfigDict(
        env_file=(str(PROJECT_ROOT / ".env"), str(BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
