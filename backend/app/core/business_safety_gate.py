from __future__ import annotations


class BusinessSafetyGate:
    def evaluate(
        self,
        *,
        action_level: str,
        trust_level: float,
        confidence_score: int,
        risk_level: str,
        is_mock: bool,
    ) -> dict:
        blocked_reasons: list[str] = []
        allowed = True
        normalized_action = action_level.upper()
        if normalized_action == "KILL":
            allowed = False
            blocked_reasons.append("执行等级为 KILL，禁止执行")
        if risk_level == "high" and normalized_action == "AUTO_LIST":
            allowed = False
            blocked_reasons.append("高风险决策禁止自动上架")
        if is_mock and normalized_action in {"SCALE", "AUTO_LIST"}:
            allowed = False
            blocked_reasons.append("mock 数据禁止进入 SCALE 或 AUTO_LIST")
        if confidence_score < 60 and normalized_action in {"TEST", "SCALE", "AUTO_LIST"}:
            allowed = False
            blocked_reasons.append("AI 置信度过低，禁止进入可执行动作")
        if trust_level < 0.6 and normalized_action in {"TEST", "SCALE", "AUTO_LIST"}:
            allowed = False
            blocked_reasons.append("数据可信度过低，禁止进入高执行级别")
        return {
            "allowed": allowed,
            "blocked_reasons": blocked_reasons,
            "final_listing_permission": allowed and normalized_action == "AUTO_LIST",
        }


business_safety_gate = BusinessSafetyGate()
