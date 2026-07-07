from __future__ import annotations

from typing import Any

from app.core.contracts import DataTrustReport


class DataTrustLayer:
    SOURCE_WEIGHT = {
        "real": 1.0,
        "cached": 0.82,
        "estimated": 0.68,
        "mock": 0.35,
    }

    def evaluate(
        self,
        *,
        data: Any,
        source_type: str,
        freshness_score: float,
        confidence_score: float,
    ) -> DataTrustReport:
        normalized_source = source_type.lower()
        freshness = self._clamp(freshness_score)
        confidence = self._clamp(confidence_score)
        source_weight = self.SOURCE_WEIGHT.get(normalized_source, self.SOURCE_WEIGHT["estimated"])
        trust_level = self._clamp((freshness * 0.35) + (confidence * 0.45) + (source_weight * 0.20))
        is_mock = normalized_source == "mock"
        is_expired = freshness < 0.35
        fallback_marked = is_mock or is_expired
        return DataTrustReport(
            data=data,
            source_type=normalized_source,
            freshness_score=freshness,
            confidence_score=confidence,
            trust_level=trust_level,
            confidence=confidence,
            is_mock=is_mock,
            is_expired=is_expired,
            fallback_marked=fallback_marked,
        )

    def aggregate(self, *reports: DataTrustReport) -> DataTrustReport:
        valid_reports = [report for report in reports if report is not None]
        if not valid_reports:
            return self.evaluate(data={}, source_type="estimated", freshness_score=0.5, confidence_score=0.5)
        freshness = sum(item.freshness_score for item in valid_reports) / len(valid_reports)
        confidence = sum(item.confidence_score for item in valid_reports) / len(valid_reports)
        is_mock = any(item.is_mock for item in valid_reports)
        source_type = "mock" if is_mock else "real" if all(item.source_type == "real" for item in valid_reports) else "estimated"
        data = {
            "sources": [item.source_type for item in valid_reports],
            "trust_levels": [item.trust_level for item in valid_reports],
        }
        return self.evaluate(
            data=data,
            source_type=source_type,
            freshness_score=freshness,
            confidence_score=confidence,
        )

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 4)


data_trust_layer = DataTrustLayer()
