from __future__ import annotations

import time
import json
import os
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.core.runtime import AppError, log_info


def analyze_title_with_ai(title: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY") or settings.openai_api_key
    if not api_key or api_key == "your_openai_api_key":
        raise AppError("MISSING_OPENAI_KEY", "请配置 OPENAI_API_KEY", "ai", 400)

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("OPENAI_MODEL") or settings.openai_model or "gpt-4o-mini"
    prompt = f"""
你是跨境电商选品助理。请根据商品标题输出 JSON，不要输出任何解释。

商品标题：{title}

返回格式：
{{
  "title_zh": "中文翻译",
  "core_keywords": ["关键词1", "关键词2"],
  "selling_points": ["卖点1", "卖点2", "卖点3"],
  "sourcing_keywords": ["适合拿货搜索词1", "适合拿货搜索词2"]
}}
"""

    last_error: Exception | None = None
    for attempt in range(1, 3):
        try:
            response = client.chat.completions.create(
                model=model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "你是跨境电商选品助理，只返回 JSON。"},
                    {"role": "user", "content": prompt},
                ],
            )
            output_text = response.choices[0].message.content or "{}"
            result = _normalize_analysis_result(json.loads(output_text))
            log_info(f"AI_OK | title={title} | model={model_name} | title_zh={result['title_zh']}")
            return result
        except Exception as exc:
            last_error = exc
            log_info(f"AI_RETRY | title={title} | attempt={attempt} | error={exc}")
            if attempt < 2:
                time.sleep(1.5)

    reason = str(last_error) if last_error else "未知 AI 错误"
    raise AppError("AI_CALL_FAILED", reason, "ai", 502) from last_error


def _normalize_analysis_result(payload: dict[str, Any]) -> dict[str, Any]:
    title_zh = str(payload.get("title_zh") or "").strip()
    core_keywords = _normalize_string_list(payload.get("core_keywords"))
    selling_points = _normalize_string_list(payload.get("selling_points"))
    sourcing_keywords = _normalize_string_list(payload.get("sourcing_keywords"))

    if not title_zh:
        raise ValueError("AI 没有返回有效的中文翻译")

    return {
        "title_zh": title_zh,
        "core_keywords": core_keywords,
        "selling_points": selling_points,
        "sourcing_keywords": sourcing_keywords,
    }


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized
