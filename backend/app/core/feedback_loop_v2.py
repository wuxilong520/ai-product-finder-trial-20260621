from __future__ import annotations

from collections import defaultdict
from statistics import mean


class FeedbackLoopV2:
    def __init__(self) -> None:
        self._records: dict[str, list[dict]] = defaultdict(list)

    def record(
        self,
        *,
        decision_id: str,
        keyword: str,
        market: str,
        listing_result: str,
        publish_success_rate: float,
        conversion_rate: float,
        profit_actual: float,
        profit_predicted: float,
        platform_performance: dict | None = None,
    ) -> dict:
        error_delta = round(float(profit_actual) - float(profit_predicted), 4)
        payload = {
            "decision_id": decision_id,
            "keyword": keyword,
            "market": market,
            "listing_result": listing_result,
            "publish_success_rate": round(float(publish_success_rate), 4),
            "conversion_rate": round(float(conversion_rate), 4),
            "profit_actual": round(float(profit_actual), 4),
            "profit_predicted": round(float(profit_predicted), 4),
            "error_delta": error_delta,
            "platform_performance": platform_performance or {},
            "feedback_signal": {
                "decision_id": decision_id,
                "actual_profit": round(float(profit_actual), 4),
                "predicted_profit": round(float(profit_predicted), 4),
                "error_delta": error_delta,
                "platform_performance": platform_performance or {},
            },
        }
        self._records[f"{market}:{keyword}".lower()].append(payload)
        return payload

    def list_records(self) -> list[dict]:
        items: list[dict] = []
        for group in self._records.values():
            items.extend(group)
        return items

    def get_records(self, *, keyword: str, market: str) -> list[dict]:
        return list(self._records.get(f"{market}:{keyword}".lower(), []))

    def latest_signal(self, *, keyword: str, market: str) -> dict:
        items = self.get_records(keyword=keyword, market=market)
        return items[-1] if items else {}

    def metrics(self) -> dict:
        items = self.list_records()
        if not items:
            return {
                "gmv_estimate": 0.0,
                "conversion_rate": 0.0,
                "execution_success_rate": 0.0,
                "ai_decision_accuracy": 0.0,
            }
        gmv_estimate = round(sum(max(item["profit_actual"], 0) for item in items), 4)
        conversion_rate = round(mean(item["conversion_rate"] for item in items), 4)
        execution_success_rate = round(mean(item["publish_success_rate"] for item in items), 4)
        accuracy_values = []
        for item in items:
            predicted = abs(float(item["profit_predicted"]))
            delta = abs(float(item["error_delta"]))
            if predicted <= 0:
                accuracy_values.append(0.0)
            else:
                accuracy_values.append(max(0.0, 1 - (delta / predicted)))
        ai_decision_accuracy = round(mean(accuracy_values), 4)
        return {
            "gmv_estimate": gmv_estimate,
            "conversion_rate": conversion_rate,
            "execution_success_rate": execution_success_rate,
            "ai_decision_accuracy": ai_decision_accuracy,
        }


feedback_loop_v2 = FeedbackLoopV2()
