from __future__ import annotations

from datetime import datetime, timezone


class DataQualityEngine:
    def evaluate(self, *, source_type: str, timestamp: datetime | None, history_weight: float = 0.5) -> dict:
        truth_level = self._truth_level(source_type)
        confidence_score = self._confidence_score(source_type)
        freshness_score = self._freshness_score(timestamp)
        reliability_score = max(0.0, min(1.0, (confidence_score * 0.6) + (freshness_score * 0.25) + (history_weight * 0.15)))
        return {
            "truth_level": truth_level,
            "confidence_score": round(confidence_score, 4),
            "freshness_score": round(freshness_score, 4),
            "reliability_score": round(reliability_score, 4),
        }

    def _truth_level(self, source_type: str) -> str:
        if source_type in {"api", "provider_amazon", "provider_shopify", "provider_tiktok"}:
            return "real"
        if source_type in {"provider_1688", "estimated", "imported"}:
            return "semi_real"
        return "simulated"

    def _confidence_score(self, source_type: str) -> float:
        if source_type in {"api", "provider_amazon", "provider_shopify", "provider_tiktok"}:
            return 0.9
        if source_type in {"provider_1688", "estimated", "imported"}:
            return 0.62
        return 0.25

    def _freshness_score(self, timestamp: datetime | None) -> float:
        if not timestamp:
            return 0.3
        now = datetime.now(timezone.utc)
        age_hours = max((now - timestamp).total_seconds() / 3600, 0)
        if age_hours <= 1:
            return 1.0
        if age_hours <= 24:
            return 0.8
        if age_hours <= 72:
            return 0.6
        if age_hours <= 168:
            return 0.4
        return 0.2


data_quality_engine = DataQualityEngine()
