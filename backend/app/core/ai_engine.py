from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib
import json
import os
from typing import Literal

from app.core.environment_manager import EnvironmentName, environment_manager
from app.core.runtime import AppError, log_info


class AIEngineBase(ABC):
    engine_name: str
    engine_type: Literal["real", "mock"]
    is_production_safe: bool

    @abstractmethod
    def complete_result(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    def complete_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        raise NotImplementedError


class EngineHardBlockError(AppError):
    def __init__(self, message: str):
        super().__init__(
            "AI_ENGINE_HARD_BLOCK",
            message,
            "ai_engine",
            503,
        )


@dataclass(frozen=True)
class EngineExecutionContext:
    env: str
    engine_type: Literal["real", "mock"]
    is_production_safe: bool
    fallback_allowed: bool


class RealAIEngine(AIEngineBase):
    engine_name = "real_ai_engine"
    engine_type: Literal["real", "mock"] = "real"
    is_production_safe = True

    def is_available(
        self,
        *,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
    ) -> bool:
        from app.services.ai_gateway import ai_gateway_service

        targets = ai_gateway_service.list_available_targets(
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
        )
        return len(targets) > 0

    def complete_result(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        from app.services.ai_gateway import ai_gateway_service

        return ai_gateway_service.chat_json(
            task_name=task_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
            allow_fallback=True,
        )

    def complete_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        result = self.complete_result(
            task_name=task_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
            use_live_gateway=use_live_gateway,
        )
        payload = result.get("payload")
        if not isinstance(payload, dict):
            raise EngineHardBlockError("真实 AI 返回结果不是结构化 JSON，已阻断调用。")
        return payload


class MockAIEngine(AIEngineBase):
    engine_name = "mock_ai_engine"
    engine_type: Literal["real", "mock"] = "mock"
    is_production_safe = False

    def complete_result(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        payload = self.complete_json(
            task_name=task_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
            use_live_gateway=use_live_gateway,
        )
        return {
            "provider_id": "mock",
            "provider_name": "Mock AI Engine",
            "model_name": "mock-json-engine",
            "payload": payload,
        }

    def complete_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        seed_text = json.dumps(
            {
                "task_name": task_name,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "context": context,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        digest = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
        base_score = 55 + int(digest[:2], 16) % 35
        keyword = str(context.get("keyword") or "sample")
        market = str(context.get("market") or "amazon")
        if task_name == "analysis":
            cost_data = context.get("cost_data", {}) or {}
            market_data = context.get("market_data", {}) or {}
            competition_data = context.get("competition_data", {}) or {}
            estimated_profit = round(float(cost_data.get("estimated_profit") or 0), 2)
            competition_score = int(
                competition_data.get("competition_score")
                or market_data.get("competition_score")
                or 50
            )
            recommend = base_score >= 68 and estimated_profit > 0
            risk_level = "low" if base_score >= 78 and competition_score <= 55 else "medium" if base_score >= 65 else "high"
            action = "list" if recommend and estimated_profit >= 15 else "test" if recommend else "ignore"
            return {
                "score": base_score,
                "recommend": recommend,
                "risk": risk_level,
                "profit_estimate": estimated_profit,
                "reasoning": f"{keyword} 在 {market} 有可验证趋势，当前利润测算为 {estimated_profit:.2f}。",
                "action": action,
                "trace": [
                    "market_data_loaded",
                    "supply_data_loaded",
                    "profit_estimated",
                    "ai_analysis_completed",
                ],
            }
        if task_name == "decision":
            strategy_mode = str(context.get("strategy_mode") or "sourcing")
            analysis_context = context.get("analysis_context", {}) or {}
            data_trust = context.get("data_trust", {}) or {}
            business_constraints = context.get("business_constraints", {}) or {}
            execution_policy = context.get("execution_policy", {}) or {}
            trust_level = float(data_trust.get("trust_level") or data_trust.get("overall", {}).get("trust_level") or 0.5)
            trust_adjusted_score = round(base_score * (0.85 if trust_level < 0.6 else 1.0), 2)
            verdict = "go" if trust_adjusted_score >= 70 else "watch"
            risk_level = "low" if trust_adjusted_score >= 75 else "medium" if trust_adjusted_score >= 60 else "high"
            recommended_price = round(float(analysis_context.get("suggested_price") or context.get("suggested_price") or 49.9), 2)
            profit_estimate = round(float(analysis_context.get("estimated_profit") or context.get("estimated_profit") or 0), 2)
            mock_flag = bool(data_trust.get("is_mock") or data_trust.get("overall", {}).get("is_mock"))
            allowed_actions = list(execution_policy.get("allowed_actions") or ["WATCH", "TEST", "SCALE", "AUTO_LIST"])
            action_plan = {
                "sourcing": [
                    "先验证市场需求是否持续",
                    "确认供应拿货价是否真实",
                    "确认利润是否能覆盖平台成本",
                ],
                "listing": [
                    "确认售价区间",
                    "确认供货履约和备货",
                    "准备上架素材和文案",
                ],
                "scaling": [
                    "复核转化率和复购",
                    "复核广告投放回本周期",
                    "确认供应链能承接放量",
                ],
            }.get(strategy_mode, [])
            execution_steps = {
                "sourcing": ["看趋势", "看利润", "看风险"],
                "listing": ["建商品卡", "上架前检查", "小单测试"],
                "scaling": ["看真实利润", "看广告效率", "控制库存节奏"],
            }.get(strategy_mode, [])
            return {
                "verdict": verdict,
                "confidence_score": int(round((float(data_trust.get("confidence") or data_trust.get("overall", {}).get("confidence") or 0.6)) * 100)),
                "recommended_price": recommended_price,
                "risk_level": risk_level,
                "decision_score": float(base_score),
                "strategy_mode": strategy_mode,
                "trust_adjusted_score": trust_adjusted_score,
                "real_profit_estimate": profit_estimate,
                "action_plan": action_plan,
                "execution_steps": execution_steps,
                "feedback_keys": [
                    f"{strategy_mode}:{market}:{keyword}:listing_performance",
                    f"{strategy_mode}:{market}:{keyword}:conversion_rate",
                    f"{strategy_mode}:{market}:{keyword}:profit_actual_vs_predicted",
                    f"{strategy_mode}:{market}:{keyword}:user_behavior",
                ],
                "allowed_actions": allowed_actions,
                "listing_recommendation": "先小单验证后再扩大" if strategy_mode != "scaling" else "只有利润稳定才建议放量",
                "trusted_market_data": {
                    "keyword": keyword,
                    "market": market,
                    "summary": analysis_context.get("market_summary") or f"{keyword} 在 {market} 存在基础需求信号",
                    "trust_level": trust_level,
                    "is_mock": mock_flag,
                },
                "supply_validation": [
                    "确认供货价",
                    "确认交期",
                    "确认 MOQ",
                ],
                "reasons": [
                    f"{keyword} 在 {market} 近期有稳定搜索热度",
                    "供货价格与预计售价之间留有基础利润空间",
                    "当前竞争强度可控，适合继续验证",
                    "已纳入策略模式、数据可信度和执行限制校正" + ("，当前存在 mock 数据降权。" if mock_flag else "。"),
                ],
            }
        if task_name == "listing":
            title = f"{keyword.title()} | 商航AI 推荐上架款"
            return {
                "seo_title": title,
                "listing_title": title,
                "listing_description": f"这是一款围绕 {keyword} 需求场景整理出的 mock 上架文案，适合先做最小验证。",
                "description": f"这是一款围绕 {keyword} 需求场景整理出的 mock 上架文案，适合先做最小验证。",
                "keywords": [keyword, f"{keyword} trend", f"{market} hot item"],
                "bullet_points": [
                    "趋势方向清晰，适合先做小单验证",
                    "供货价格已预留基础利润空间",
                    "适合后续接真实平台做自动上架",
                ],
                "image_structure": [
                    "主图：白底商品图",
                    "场景图：核心使用场景",
                    "细节图：材质与尺寸说明",
                ],
                "selling_points": [
                    "围绕真实需求词生成标题",
                    "保留基础利润空间",
                    "便于后续接真实平台后一键替换",
                ],
                "tags": [keyword, market, "shanghang-ai", "mock-listing"],
            }
        return {
            "summary": f"{keyword} 在 {market} 具备基础验证价值。",
            "confidence_score": base_score,
        }


def _staging_mock_fallback_enabled() -> bool:
    return str(os.getenv("AI_STAGING_MOCK_FALLBACK", "false")).lower() == "true"


def _build_execution_context(*, engine_type: Literal["real", "mock"]) -> EngineExecutionContext:
    env = environment_manager.current()
    fallback_allowed = env == EnvironmentName.DEV.value or (
        env == EnvironmentName.STAGING.value and _staging_mock_fallback_enabled()
    )
    return EngineExecutionContext(
        env=env,
        engine_type=engine_type,
        is_production_safe=engine_type == "real",
        fallback_allowed=fallback_allowed,
    )


def resolve_ai_engine(context: EngineExecutionContext) -> AIEngineBase:
    real_engine = RealAIEngine()

    if context.env == EnvironmentName.PRODUCTION.value:
        if not real_engine.is_available():
            raise EngineHardBlockError("production 环境没有可用的真实 AI 引擎，系统已硬阻断。")
        return real_engine

    if context.env == EnvironmentName.STAGING.value:
        if real_engine.is_available():
            return real_engine
        if context.fallback_allowed:
            return MockAIEngine()
        raise EngineHardBlockError("staging 环境真实 AI 不可用，且没有显式开启 mock fallback。")

    if context.env == EnvironmentName.DEV.value:
        if context.engine_type == "real" and real_engine.is_available():
            return real_engine
        return MockAIEngine()

    raise EngineHardBlockError(f"未知环境 {context.env}，AI 引擎已阻断。")


class ProductionAwareAIEngine(AIEngineBase):
    engine_name = "production_aware_ai_engine"
    engine_type: Literal["real", "mock"] = "real"
    is_production_safe = True

    def _resolve(
        self,
        *,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
    ) -> tuple[AIEngineBase, EngineExecutionContext]:
        env = environment_manager.current()
        requested_engine_type: Literal["real", "mock"] = "real" if env != EnvironmentName.DEV.value else "mock"
        requested_context = _build_execution_context(engine_type=requested_engine_type)
        engine = resolve_ai_engine(requested_context)
        effective_context = _build_execution_context(engine_type=engine.engine_type)

        if env == EnvironmentName.PRODUCTION.value and engine.engine_type != "real":
            raise EngineHardBlockError("production 环境检测到 mock 引擎，系统已硬阻断。")

        if engine.engine_type == "real":
            real_engine = engine if isinstance(engine, RealAIEngine) else RealAIEngine()
            if not real_engine.is_available(
                preferred_provider=preferred_provider,
                preferred_model=preferred_model,
                allowed_provider_ids=allowed_provider_ids,
                allowed_model_names=allowed_model_names,
            ):
                if env == EnvironmentName.PRODUCTION.value:
                    raise EngineHardBlockError("production 环境真实 AI 不可用，禁止 fallback。")
                if env == EnvironmentName.STAGING.value and not effective_context.fallback_allowed:
                    raise EngineHardBlockError("staging 环境真实 AI 不可用，且未显式允许 fallback。")

        return engine, effective_context

    def _log_execution(
        self,
        *,
        task_name: str,
        context: EngineExecutionContext,
        engine: AIEngineBase,
    ) -> None:
        log_info(
            "AI_ENGINE_EXECUTION | "
            + json.dumps(
                {
                    "task_name": task_name,
                    "engine_name": engine.engine_name,
                    "engine_type": engine.engine_type,
                    "is_mock": engine.engine_type == "mock",
                    "env": context.env,
                    "production_safe": context.is_production_safe,
                    "fallback_allowed": context.fallback_allowed,
                },
                ensure_ascii=False,
            )
        )

    def complete_result(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        engine, execution_context = self._resolve(
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
        )
        self._log_execution(task_name=task_name, context=execution_context, engine=engine)
        return engine.complete_result(
            task_name=task_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
            use_live_gateway=use_live_gateway,
        )

    def complete_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        context: dict,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
        allowed_provider_ids: list[str] | None = None,
        allowed_model_names: list[str] | None = None,
        use_live_gateway: bool = False,
    ) -> dict:
        engine, execution_context = self._resolve(
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
        )
        self._log_execution(task_name=task_name, context=execution_context, engine=engine)
        payload = engine.complete_json(
            task_name=task_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            preferred_provider=preferred_provider,
            preferred_model=preferred_model,
            allowed_provider_ids=allowed_provider_ids,
            allowed_model_names=allowed_model_names,
            use_live_gateway=use_live_gateway,
        )
        if not isinstance(payload, dict):
            raise EngineHardBlockError("AI 输出不是结构化 JSON，系统已硬阻断。")
        return payload


ai_engine: AIEngineBase = ProductionAwareAIEngine()
