from __future__ import annotations

from collections import Counter, defaultdict

from app.core.feedback_loop_v2 import feedback_loop_v2
from app.core.execution_log_layer import execution_log_layer


class ExecutionInsightLayer:
    def summarize(self) -> dict:
        logs = execution_log_layer.list_logs()
        feedback_records = feedback_loop_v2.list_records()

        blocked_counter: Counter[str] = Counter()
        for item in logs:
            reason = item.get("blocked_reason") or item.get("decision", {}).get("execution_block_reason") or "未拦截"
            blocked_counter[reason] += 1

        listing_success_map: dict[str, list[float]] = defaultdict(list)
        profit_map: dict[str, float] = defaultdict(float)
        risk_distribution: Counter[str] = Counter()

        for item in logs:
            decision = item.get("decision", {})
            keyword = str(item.get("keyword") or decision.get("keyword") or "unknown")
            risk_distribution[str(decision.get("risk_level") or "unknown")] += 1
            platform_status = str(decision.get("platform_execution_status") or item.get("platform_execution_status") or "blocked")
            listing_success_map[keyword].append(1.0 if "queued" in platform_status or "ready" in platform_status or platform_status == "success" else 0.0)

        for record in feedback_records:
            keyword = str(record.get("keyword") or "unknown")
            profit_map[keyword] += float(record.get("profit_actual") or 0)
            listing_success_map[keyword].append(float(record.get("publish_success_rate") or 0))

        best_success = sorted(
            (
                {"keyword": keyword, "success_rate": round(sum(values) / len(values), 4)}
                for keyword, values in listing_success_map.items() if values
            ),
            key=lambda item: item["success_rate"],
            reverse=True,
        )
        most_profitable = sorted(
            ({"keyword": keyword, "profit_actual": round(value, 4)} for keyword, value in profit_map.items()),
            key=lambda item: item["profit_actual"],
            reverse=True,
        )

        return {
            "most_blocked_decisions": [
                {"reason": reason, "count": count} for reason, count in blocked_counter.most_common(5)
            ],
            "highest_listing_success": best_success[:5],
            "most_profitable_items": most_profitable[:5],
            "risk_distribution": dict(risk_distribution),
            "growth_metrics": feedback_loop_v2.metrics(),
        }


execution_insight_layer = ExecutionInsightLayer()
