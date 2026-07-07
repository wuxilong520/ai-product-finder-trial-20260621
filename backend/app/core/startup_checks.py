from __future__ import annotations

import os

from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.runtime import AppError, log_info
from app.core.production_detector import production_detector


def validate_startup_env() -> dict:
    missing = settings.missing_backend_env()
    if missing:
        raise AppError(
            "MISSING_REQUIRED_ENV",
            f"缺少必要环境变量：{', '.join(missing)}",
            "env",
            500,
        )
    if settings.is_production():
        invalid_items = []
        for label, value in {
            "BACKEND_URL": settings.backend_url,
            "FRONTEND_URL": settings.frontend_url,
            "FRONTEND_ORIGIN": settings.frontend_origin,
            "WS_URL": settings.ws_url,
            "NEXT_PUBLIC_API_BASE_URL": settings.next_public_api_base_url,
            "NEXT_PUBLIC_WS_URL": settings.next_public_ws_url,
        }.items():
            if settings.has_local_address(value):
                invalid_items.append(label)
        if invalid_items:
            raise AppError(
                "PRODUCTION_ENV_INVALID",
                f"生产环境不能使用本地地址：{', '.join(invalid_items)}",
                "env",
                500,
            )
        if settings.secret_key == "change_me_to_a_secure_secret":
            raise AppError("PRODUCTION_SECRET_INVALID", "生产环境 SECRET_KEY 不能使用默认值", "env", 500)
        if settings.first_superuser_password == "change_this_password":
            raise AppError("PRODUCTION_ADMIN_INVALID", "生产环境管理员密码不能使用默认值", "env", 500)
        if not settings.cors_origins():
            raise AppError("PRODUCTION_CORS_INVALID", "生产环境必须配置 FRONTEND_ORIGIN", "env", 500)

    return {
        "app_env": settings.app_env,
        "backend_url": settings.backend_url,
        "frontend_url": settings.frontend_url,
        "frontend_origin": settings.frontend_origin,
        "ws_url": settings.ws_url,
        "next_public_api_base_url": settings.next_public_api_base_url,
        "next_public_ws_url": settings.next_public_ws_url,
    }


def check_database_health() -> str:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:
        log_info(f"HEALTH_DB_FAIL | error={exc}")
        return "fail"
    finally:
        db.close()


def check_ai_health() -> str:
    has_ai_key = any(
        bool((os.getenv(key) or "").strip())
        for key in [
            "DEEPSEEK_API_KEY",
            "DASHSCOPE_API_KEY",
            "MOONSHOT_API_KEY",
            "ARK_API_KEY",
            "ZHIPU_API_KEY",
            "OPENAI_API_KEY",
        ]
    ) or bool((settings.openai_api_key or "").strip())
    if not has_ai_key:
        return "fail"
    if not settings.openai_model:
        return "fail"
    return "ok"


def check_crawler_health() -> str:
    try:
        from playwright.async_api import async_playwright  # noqa: F401
    except Exception as exc:
        log_info(f"HEALTH_CRAWLER_FAIL | error={exc}")
        return "fail"
    return "ok"


def collect_runtime_summary() -> dict:
    env_status = {
        "app_env": settings.app_env,
        "backend_url": bool(settings.backend_url),
        "frontend_url": bool(settings.frontend_url),
        "frontend_origin": bool(settings.frontend_origin),
        "ws_url": bool(settings.ws_url),
        "next_public_api_base_url": bool(settings.next_public_api_base_url),
        "next_public_ws_url": bool(settings.next_public_ws_url),
        "cors_origins": settings.cors_origins(),
    }
    services = {
        "database": check_database_health(),
        "ai": check_ai_health(),
        "crawler": check_crawler_health(),
    }
    status = "ok" if all(value == "ok" for value in services.values()) else "degraded"
    return {
        "status": status,
        "version": "v2",
        "env_status": env_status,
        "services": services,
        "production_detector": production_detector.detect(),
    }
