from __future__ import annotations

import os

from openai import OpenAI

from app.core.config import settings
from app.core.runtime import AppError


PROVIDER_KEY_MAP: list[tuple[str, str]] = [
    ("DEEPSEEK_API_KEY", "DeepSeek"),
    ("DASHSCOPE_API_KEY", "DashScope"),
    ("MOONSHOT_API_KEY", "Moonshot"),
    ("ARK_API_KEY", "Volcengine Ark"),
    ("ZHIPU_API_KEY", "Zhipu"),
    ("OPENAI_API_KEY", "OpenAI"),
]


def resolve_ai_credentials() -> tuple[str, str | None]:
    base_url = (os.getenv("OPENAI_BASE_URL") or settings.openai_base_url or "").strip() or None

    for env_key, _provider_name in PROVIDER_KEY_MAP:
        env_value = (os.getenv(env_key) or "").strip()
        if env_value:
            return env_value, base_url

    configured_key = (settings.openai_api_key or "").strip()
    if configured_key and configured_key != "your_openai_api_key":
        return configured_key, base_url

    raise AppError("MISSING_OPENAI_KEY", "请配置可用的 AI API KEY", "ai", 400)


def build_ai_client() -> OpenAI:
    api_key, base_url = resolve_ai_credentials()
    return OpenAI(api_key=api_key, base_url=base_url)
