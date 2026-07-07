from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.contracts import DecisionRecord, ExplainPacket, ProfitBreakdown


class ExplainEngineBase(ABC):
    @abstractmethod
    def build(self, *, decision: DecisionRecord, profit: ProfitBreakdown) -> ExplainPacket:
        raise NotImplementedError


class ExplainEngine(ExplainEngineBase):
    def build(self, *, decision: DecisionRecord, profit: ProfitBreakdown) -> ExplainPacket:
        risk_notes = [
            f"当前风险等级：{decision.risk_level}",
            "当前为 mock 数据流程，真实平台接入后需要重新校准价格和竞争强度。"
            if bool(decision.data_trust.get("is_mock"))
            else "当前决策已经带入数据可信度校正。",
        ]
        next_actions = decision.execution_steps or [
            "继续验证关键词搜索趋势",
            "继续核对 1688 供应稳定性",
            "确认上架文案后再进入发布流程",
        ]
        return ExplainPacket(
            summary=f"{decision.keyword} 当前建议为 {decision.verdict}，策略模式 {decision.strategy_mode}，真实利润预估 {decision.real_profit_estimate:.2f} 元。",
            reasons=decision.reasons,
            risk_notes=risk_notes,
            next_actions=next_actions,
        )


explain_engine: ExplainEngineBase = ExplainEngine()
