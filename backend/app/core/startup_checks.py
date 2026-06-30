from __future__ import annotations

import os

from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.runtime import AppError, log_info


def validate_startup_env() -> dict:
    missing = settings.missing_backend_env()
    if missing:
        raise AppError(
            "MISSING_REQUIRED_ENV",
            f"缺少必要环境变量：{', '.join(missing)}",
            "env",
            500,
        )

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
    }
