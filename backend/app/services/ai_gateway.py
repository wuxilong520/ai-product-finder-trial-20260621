from __future__ import annotations

from dataclasses import dataclass
import os
import time
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.core.runtime import AppError, log_info


@dataclass(frozen=True)
class AIProviderProfile:
    provider_id: str
    display_name: str
    key_env: str
    model_env: str
    base_url_env: str
    default_model: str
    default_base_url: str | None = None


@dataclass(frozen=True)
class AIExecutionTarget:
    provider_id: str
    display_name: str
    api_key: str
    model_name: str
    base_url: str | None


PROVIDER_PROFILES: list[AIProviderProfile] = [
    AIProviderProfile(
        provider_id="deepseek",
        display_name="DeepSeek",
        key_env="DEEPSEEK_API_KEY",
        model_env="DEEPSEEK_MODEL",
        base_url_env="DEEPSEEK_BASE_URL",
        default_model="deepseek-chat",
        default_base_url="https://api.deepseek.com",
    ),
    AIProviderProfile(
        provider_id="qwen",
        display_name="Qwen",
        key_env="DASHSCOPE_API_KEY",
        model_env="DASHSCOPE_MODEL",
        base_url_env="DASHSCOPE_BASE_URL",
        default_model="qwen-plus",
        default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
    AIProviderProfile(
        provider_id="kimi",
        display_name="Kimi",
        key_env="MOONSHOT_API_KEY",
        model_env="MOONSHOT_MODEL",
        base_url_env="MOONSHOT_BASE_URL",
        default_model="moonshot-v1-8k",
        default_base_url="https://api.moonshot.cn/v1",
    ),
    AIProviderProfile(
        provider_id="doubao",
        display_name="Doubao",
        key_env="ARK_API_KEY",
        model_env="ARK_MODEL",
        base_url_env="ARK_BASE_URL",
        default_model="doubao-1-5-lite-32k-250115",
        default_base_url="https://ark.cn-beijing.volces.com/api/v3",
    ),
    AIProviderProfile(
        provider_id="zhipu",
        display_name="Zhipu",
        key_env="ZHIPU_API_KEY",
        model_env="ZHIPU_MODEL",
        base_url_env="ZHIPU_BASE_URL",
        default_model="glm-4-flash",
        default_base_url="https://open.bigmodel.cn/api/paas/v4",
    ),
    AIProviderProfile(
        provider_id="openai",
        display_name="OpenAI",
        key_env="OPENAI_API_KEY",
        model_env="OPENAI_MODEL",
        base_url_env="OPENAI_BASE_URL",
        default_model="gpt-4o-mini",
        default_base_url=None,
    ),
]


class AIGatewayService:
    def list_available_targets(
        self,
        *,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
    ) -> list[AIExecutionTarget]:
        profiles = PROVIDER_PROFILES[:]
        if allowed_provider_ids is not None:
            allowed = set(allowed_provider_ids)
            profiles = [item for item in profiles if item.provider_id in allowed]
        if preferred_provider:
            profiles.sort(key=lambda item: item.provider_id != preferred_provider)

        targets: list[AIExecutionTarget] = []
        allowed_models = set(allowed_model_names or [])
        for profile in profiles:
            api_key = (os.getenv(profile.key_env) or "").strip()
            if not api_key and profile.provider_id == "openai":
                api_key = (settings.openai_api_key or "").strip()
            if not api_key:
                continue

            base_url = (os.getenv(profile.base_url_env) or "").strip() or None
            if not base_url and profile.provider_id == "openai":
                base_url = (settings.openai_base_url or "").strip() or None
            if not base_url:
                base_url = profile.default_base_url

            model_name = preferred_model or (os.getenv(profile.model_env) or "").strip()
            if not model_name and profile.provider_id == "openai":
                model_name = (settings.openai_model or "").strip()
            if not model_name:
                model_name = profile.default_model
            if allowed_models and model_name not in allowed_models:
                continue

            targets.append(
                AIExecutionTarget(
                    provider_id=profile.provider_id,
                    display_name=profile.display_name,
                    api_key=api_key,
                    model_name=model_name,
                    base_url=base_url,
                )
            )
        return targets

    def chat_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        allow_fallback: bool = True,
    ) -> dict[str, Any]:
        targets = self.list_available_targets(
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
        )
        if not targets:
            if allowed_provider_ids or allowed_model_names:
                raise AppError("AI_PROVIDER_NOT_READY", "当前套餐允许的 AI 模型还没有配置好，请联系管理员。", "ai", 503)
            raise AppError("MISSING_OPENAI_KEY", "请先配置至少一个可用的 AI 提供商 Key", "ai", 400)

        last_error: Exception | None = None
        for index, target in enumerate(targets):
            if index > 0 and not allow_fallback:
                break
            try:
                client = OpenAI(api_key=target.api_key, base_url=target.base_url)
                response = client.chat.completions.create(
                    model=target.model_name,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                output_text = response.choices[0].message.content or "{}"
                log_info(
                    "AI_GATEWAY_OK | "
                    f"task={task_name} | provider={target.provider_id} | model={target.model_name}"
                )
                import json

                return {
                    "provider_id": target.provider_id,
                    "provider_name": target.display_name,
                    "model_name": target.model_name,
                    "payload": json.loads(output_text),
                }
            except Exception as exc:
                last_error = exc
                log_info(
                    "AI_GATEWAY_FAILOVER | "
                    f"task={task_name} | provider={target.provider_id} | model={target.model_name} | error={exc}"
                )
                time.sleep(0.8)
                continue

        reason = str(last_error) if last_error else "未知 AI 调用错误"
        raise AppError("AI_GATEWAY_FAILED", reason, "ai", 502) from last_error


ai_gateway_service = AIGatewayService()
