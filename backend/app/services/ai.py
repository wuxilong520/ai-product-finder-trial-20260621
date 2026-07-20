from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.runtime import log_info
from app.core.ai_engine import ai_engine
from app.services.ai_model_policy import ai_model_policy_service


def analyze_title_with_ai(db: Session, title: str, *, workspace_id: int | None = None) -> dict:
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
    result = ai_engine.complete_result(
        task_name="analyze_title",
        system_prompt="你是跨境电商选品助理，只返回 JSON。",
        user_prompt=prompt,
        context={"title": title, "workspace_id": workspace_id},
        allowed_provider_ids=ai_model_policy_service.get_allowed_provider_ids(db, workspace_id=workspace_id),
        allowed_model_names=ai_model_policy_service.get_allowed_model_names(db, workspace_id=workspace_id),
        use_live_gateway=True,
    )
    normalized = _normalize_analysis_result(result["payload"])
    normalized["provider_id"] = result["provider_id"]
    normalized["provider_name"] = result["provider_name"]
    normalized["model_name"] = result["model_name"]
    log_info(
        "AI_OK | "
        f"title={title} | provider={result['provider_id']} | model={result['model_name']} | title_zh={normalized['title_zh']}"
    )
    return normalized


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
