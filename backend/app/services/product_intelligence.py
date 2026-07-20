from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.ai_engine import ai_engine
from app.core.runtime import AppError, log_info
from app.services.ai_model_policy import ai_model_policy_service


def analyze_product_intelligence(
    db: Session,
    *,
    title: str,
    price: str | float | None,
    images: list[str],
    rating: str | float | None,
    review_count: str | int | None,
    source_url: str,
    sales: str | None = None,
    workspace_id: int | None = None,
) -> dict:
    payload = {
        "title": title or "",
        "price": _normalize_price_text(price),
        "images": images[:5],
        "rating": _normalize_number_text(rating),
        "review_count": _normalize_int_text(review_count),
        "sales": _normalize_int_text(sales),
        "source_url": source_url,
        "platform": _detect_platform(source_url),
    }

    prompt = f"""
你是跨境电商选品分析助手。
请你根据下面这个真实商品信息，输出严格 JSON，不要输出任何解释，不要输出 Markdown。

评分要求：
1. 利润潜力：0-30分
2. 竞争强度：0-30分
3. 商品吸引力：0-20分
4. 销售信号：0-20分

你的总分必须是 0-100 的整数。

输出格式必须严格等于：
{{
  "product_score": 0,
  "profit_estimate": "string",
  "competition_level": "low",
  "selling_potential": "weak",
  "recommendation": "ignore",
  "reason": ["原因1", "原因2", "原因3"]
}}

商品数据：
{json.dumps(payload, ensure_ascii=False)}
"""
    result = ai_engine.complete_result(
        task_name="product_intelligence",
        system_prompt="你是跨境电商选品分析助手，只返回 JSON。",
        user_prompt=prompt,
        context=payload,
        allowed_provider_ids=ai_model_policy_service.get_allowed_provider_ids(db, workspace_id=workspace_id),
        allowed_model_names=ai_model_policy_service.get_allowed_model_names(db, workspace_id=workspace_id),
        use_live_gateway=True,
    )
    normalized = _normalize_ai_intelligence_result(result["payload"])
    normalized["provider_id"] = result["provider_id"]
    normalized["provider_name"] = result["provider_name"]
    normalized["model_name"] = result["model_name"]
    log_info(
        "PRODUCT_INTELLIGENCE_OK | "
        f"title={title} | provider={result['provider_id']} | model={result['model_name']} | score={normalized['product_score']} | rec={normalized['recommendation']}"
    )
    return normalized


def _normalize_ai_intelligence_result(payload: dict[str, Any]) -> dict[str, Any]:
    product_score = int(max(0, min(100, int(payload.get("product_score") or 0))))
    profit_estimate = str(payload.get("profit_estimate") or "").strip()
    competition_level = _normalize_competition_level(payload.get("competition_level"))
    selling_potential = _normalize_selling_potential(payload.get("selling_potential"))
    recommendation = _normalize_recommendation(payload.get("recommendation"))
    reason = payload.get("reason")

    if competition_level not in {"low", "medium", "high"}:
        raise AppError("AI_CALL_FAILED", "AI 返回的 competition_level 不合法", "ai", 502)
    if selling_potential not in {"weak", "ok", "strong"}:
        raise AppError("AI_CALL_FAILED", "AI 返回的 selling_potential 不合法", "ai", 502)
    if recommendation not in {"sell", "monitor", "ignore"}:
        raise AppError("AI_CALL_FAILED", "AI 返回的 recommendation 不合法", "ai", 502)

    normalized_reasons = _normalize_reason_list(reason)
    if not profit_estimate:
        raise AppError("AI_CALL_FAILED", "AI 没有返回有效的 profit_estimate", "ai", 502)
    if not normalized_reasons:
        raise AppError("AI_CALL_FAILED", "AI 没有返回有效的 reason", "ai", 502)

    return {
        "product_score": product_score,
        "profit_estimate": profit_estimate,
        "competition_level": competition_level,
        "selling_potential": selling_potential,
        "recommendation": recommendation,
        "reason": normalized_reasons,
    }


def _normalize_competition_level(value: Any) -> str:
    raw_value = str(value or "").strip().lower()
    alias_map = {
        "low": "low",
        "weak": "low",
        "small": "low",
        "light": "low",
        "medium": "medium",
        "moderate": "medium",
        "normal": "medium",
        "average": "medium",
        "ok": "medium",
        "high": "high",
        "strong": "high",
        "heavy": "high",
        "intense": "high",
    }
    return alias_map.get(raw_value, raw_value)


def _normalize_selling_potential(value: Any) -> str:
    raw_value = str(value or "").strip().lower()
    alias_map = {
        "weak": "weak",
        "low": "weak",
        "poor": "weak",
        "limited": "weak",
        "ok": "ok",
        "medium": "ok",
        "moderate": "ok",
        "normal": "ok",
        "average": "ok",
        "considerable": "ok",
        "strong": "strong",
        "high": "strong",
        "great": "strong",
        "excellent": "strong",
    }
    return alias_map.get(raw_value, raw_value)


def _normalize_recommendation(value: Any) -> str:
    raw_value = str(value or "").strip().lower()
    alias_map = {
        "sell": "sell",
        "launch": "sell",
        "recommend": "sell",
        "recommended": "sell",
        "monitor": "monitor",
        "watch": "monitor",
        "observe": "monitor",
        "consider": "monitor",
        "hold": "monitor",
        "ignore": "ignore",
        "skip": "ignore",
        "reject": "ignore",
        "avoid": "ignore",
        "not_recommended": "ignore",
    }
    return alias_map.get(raw_value, raw_value)


def _normalize_reason_list(value: Any) -> list[str]:
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return items
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_price_text(value: str | float | None) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    return str(value).strip()


def _normalize_number_text(value: str | float | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_int_text(value: str | int | None) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    text = str(value).strip()
    match = re.search(r"([\d,.kK]+)", text)
    return match.group(1) if match else text


def _detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "amazon." in host:
        return "amazon"
    if "aliexpress." in host:
        return "aliexpress"
    return "shopify"
