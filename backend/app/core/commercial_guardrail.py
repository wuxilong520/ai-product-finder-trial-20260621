from __future__ import annotations


class CommercialGuardrail:
    def evaluate(self, *, product_mode: str, risk_level: str, is_mock: bool, launch_allowed: bool, production_lock: bool = False) -> dict:
        blockers: list[str] = []
        if not launch_allowed:
            blockers.append("上线检查清单未通过")
        if product_mode != "production_mode":
            blockers.append("当前不是 production_mode，禁止真实自动执行")
        if str(risk_level).lower() == "high":
            blockers.append("当前风险等级高，禁止误上线")
        if is_mock:
            blockers.append("当前仍有 mock 数据，禁止当成真实商业决策")
        if production_lock and is_mock:
            blockers.append("生产锁已启用，禁止 mock 注入")
        return {
            "allowed": len(blockers) == 0,
            "blocking_factors": blockers,
        }


commercial_guardrail = CommercialGuardrail()
