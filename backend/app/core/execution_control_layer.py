from __future__ import annotations

from enum import Enum

from app.core.business_safety_gate import business_safety_gate


class ActionLevel(str, Enum):
    KILL = "KILL"
    WATCH = "WATCH"
    TEST = "TEST"
    SCALE = "SCALE"
    AUTO_LIST = "AUTO_LIST"


class ExecutionControlLayer:
    def evaluate(self, decision) -> dict:
        trust_level = float(decision.data_trust.get("trust_level", 0))
        is_mock = bool(decision.data_trust.get("is_mock", False))
        risk_level = str(decision.risk_level).lower()
        confidence_score = int(decision.confidence_score)

        action_level = self._derive_action_level(
            trust_adjusted_score=float(decision.trust_adjusted_score),
            confidence_score=confidence_score,
            risk_level=risk_level,
        )
        override_history: list[dict] = []
        block_reason = ""

        if trust_level < 0.6 and action_level != ActionLevel.KILL:
            override_history.append({"rule": "trust_level_lt_0.6", "from": action_level.value, "to": ActionLevel.WATCH.value})
            action_level = ActionLevel.WATCH
            block_reason = "数据可信度低于 0.6，强制降为 WATCH。"

        if is_mock and action_level in {ActionLevel.SCALE, ActionLevel.AUTO_LIST}:
            override_history.append({"rule": "is_mock_max_test", "from": action_level.value, "to": ActionLevel.TEST.value})
            action_level = ActionLevel.TEST
            block_reason = "当前数据含 mock，最高只能到 TEST。"

        if risk_level == "high" and action_level == ActionLevel.AUTO_LIST:
            override_history.append({"rule": "high_risk_block_auto_list", "from": action_level.value, "to": ActionLevel.TEST.value})
            action_level = ActionLevel.TEST
            block_reason = "高风险决策，禁止 AUTO_LIST。"

        gate_result = business_safety_gate.evaluate(
            action_level=action_level.value,
            trust_level=trust_level,
            confidence_score=confidence_score,
            risk_level=risk_level,
            is_mock=is_mock,
        )
        execution_allowed = bool(gate_result["allowed"]) and action_level != ActionLevel.KILL
        if not execution_allowed and not block_reason:
            block_reason = "；".join(gate_result["blocked_reasons"]) or "执行安全闸门未通过"

        return {
            "action_level": action_level.value,
            "execution_allowed": execution_allowed,
            "execution_block_reason": block_reason,
            "safety_gate_result": gate_result,
            "final_listing_permission": bool(gate_result["final_listing_permission"]),
            "override_history": override_history,
        }

    def build_execution_policy(self, *, trust_level: float, is_mock: bool, risk_level: str) -> dict:
        allowed_actions = [ActionLevel.WATCH.value, ActionLevel.TEST.value, ActionLevel.SCALE.value, ActionLevel.AUTO_LIST.value]
        if trust_level < 0.6:
            allowed_actions = [ActionLevel.WATCH.value]
        elif is_mock:
            allowed_actions = [ActionLevel.WATCH.value, ActionLevel.TEST.value]
        elif str(risk_level).lower() == "high":
            allowed_actions = [ActionLevel.WATCH.value, ActionLevel.TEST.value, ActionLevel.SCALE.value]
        return {
            "execution_policy": "AI output must pass execution control before final action",
            "allowed_actions": allowed_actions,
            "safety_constraints": {
                "trust_level_min_for_action": 0.6,
                "mock_data_max_action": ActionLevel.TEST.value,
                "high_risk_block_auto_list": True,
            },
        }

    def _derive_action_level(self, *, trust_adjusted_score: float, confidence_score: int, risk_level: str) -> ActionLevel:
        if confidence_score < 45 or trust_adjusted_score < 40:
            return ActionLevel.KILL
        if trust_adjusted_score < 60 or risk_level == "high":
            return ActionLevel.WATCH
        if trust_adjusted_score < 72:
            return ActionLevel.TEST
        if trust_adjusted_score < 86:
            return ActionLevel.SCALE
        return ActionLevel.AUTO_LIST


execution_control_layer = ExecutionControlLayer()
