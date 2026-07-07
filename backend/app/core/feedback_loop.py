from __future__ import annotations

from collections import defaultdict


class ExecutionFeedbackLayer:
    def __init__(self) -> None:
        self._store: dict[str, list[dict]] = defaultdict(list)

    def register_feedback_keys(self, *, keyword: str, market: str, strategy_mode: str) -> list[str]:
        prefix = f"{strategy_mode}:{market}:{keyword}".replace(" ", "_").lower()
        return [
            f"{prefix}:listing_performance",
            f"{prefix}:conversion_rate",
            f"{prefix}:profit_actual_vs_predicted",
            f"{prefix}:user_behavior",
        ]

    def record_feedback(
        self,
        *,
        feedback_key: str,
        listing_performance: dict | None = None,
        conversion_rate: float | None = None,
        profit_actual_vs_predicted: dict | None = None,
        user_behavior: dict | None = None,
    ) -> dict:
        payload = {
            "feedback_key": feedback_key,
            "listing_performance": listing_performance or {},
            "conversion_rate": conversion_rate,
            "profit_actual_vs_predicted": profit_actual_vs_predicted or {},
            "user_behavior": user_behavior or {},
        }
        self._store[feedback_key].append(payload)
        return payload

    def get_feedback(self, feedback_key: str) -> list[dict]:
        return list(self._store.get(feedback_key, []))


feedback_loop = ExecutionFeedbackLayer()
