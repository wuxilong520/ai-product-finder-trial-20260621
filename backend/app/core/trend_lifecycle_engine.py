from __future__ import annotations

from statistics import mean


class TrendLifecycleEngine:
    def classify(
        self,
        *,
        trend_strength: float,
        growth_signals: list[float] | None = None,
        previous_market_score: float | None = None,
    ) -> str:
        average_growth = mean([float(item or 0) for item in (growth_signals or [])] or [0.0])
        previous = float(previous_market_score or 0)
        current = float(trend_strength or 0)

        if current >= 75 and average_growth >= 12:
            return "growing"
        if current >= 60 and average_growth >= 4:
            return "stable"
        if current >= 45 and average_growth > 0 and previous <= 0:
            return "emerging"
        if previous > 0 and current < previous * 0.8:
            return "declining"
        if current < 40:
            return "declining"
        return "stable"


trend_lifecycle_engine = TrendLifecycleEngine()
