from __future__ import annotations

from statistics import mean, pstdev
from typing import Any

from pydantic import BaseModel, Field


class MarketEvidence(BaseModel):
    source: str
    data_status: str
    source_kind: str = "public_market"
    confidence: float = Field(default=0.0, ge=0, le=1)
    timestamp: str = ""
    signal_strength: float = Field(default=0.0, ge=0, le=100)


class MarketConfidenceScore(BaseModel):
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    source_reliability: dict[str, float] = Field(default_factory=dict)
    evidence_sources: list[dict[str, Any]] = Field(default_factory=list)
    real_data_ratio: float = Field(default=0.0, ge=0, le=1)
    risk_flags: list[str] = Field(default_factory=list)


class MarketConfidenceEngine:
    CORE_REALITY_SOURCES = {"amazon", "bing", "walmart", "reddit", "youtube"}

    STATUS_WEIGHTS = {
        "real": 1.0,
        "limited": 0.75,
        "partial": 0.6,
        "fallback": 0.2,
        "not_configured": 0.0,
        "mock": 0.0,
    }

    SOURCE_WEIGHTS = {
        "shopify": 1.0,
        "amazon": 0.9,
        "tiktok": 0.85,
        "reddit": 0.85,
        "youtube": 0.8,
        "walmart": 0.75,
        "ebay": 0.7,
        "bing": 0.7,
        "meta": 0.7,
        "google": 0.2,
        "pinterest": 0.55,
    }

    SOURCE_KIND_WEIGHTS = {
        "authorized_commercial": 1.0,
        "commercial_api": 0.9,
        "public_market": 0.5,
    }

    def evaluate(self, signals: dict[str, dict]) -> MarketConfidenceScore:
        weighted_signal_sum = 0.0
        weight_sum = 0.0
        source_reliability: dict[str, float] = {}
        evidence_sources: list[dict[str, Any]] = []
        real_weight_total = 0.0

        for source, payload in signals.items():
            source_weight = float(self.SOURCE_WEIGHTS.get(source, 0.5))
            status = str(payload.get("data_status") or "fallback").lower()
            status_weight = float(self.STATUS_WEIGHTS.get(status, 0.2))
            source_kind = str(payload.get("source_kind") or "public_market")
            source_kind_weight = float(self.SOURCE_KIND_WEIGHTS.get(source_kind, 0.5))
            signal_strength = float(payload.get("value") or 0)
            confidence = float(payload.get("confidence") or 0)
            data_quality = confidence
            reliability = round(source_weight * status_weight * source_kind_weight * data_quality, 4)

            weighted_signal_sum += source_weight * status_weight * source_kind_weight * signal_strength
            weight_sum += source_weight
            if status == "real":
                real_weight_total += source_weight

            source_reliability[source] = reliability
            evidence_sources.append(
                {
                    "source": source,
                    "data_status": status,
                    "source_kind": source_kind,
                    "signal_strength": round(signal_strength, 2),
                    "confidence": round(confidence, 4),
                    "reliability": reliability,
                    "timestamp": str(payload.get("timestamp") or ""),
                }
            )

        confidence_score = round(max(0.0, min(1.0, (weighted_signal_sum / weight_sum) / 100 if weight_sum else 0.0)), 4)
        real_data_ratio = round(max(0.0, min(1.0, real_weight_total / weight_sum if weight_sum else 0.0)), 4)

        risk_flags: list[str] = []
        if confidence_score < 0.6:
            risk_flags.append("low_market_confidence")
        if real_data_ratio < 0.5:
            risk_flags.append("low_real_ratio")
        if any(item.get("data_status") == "fallback" for item in evidence_sources):
            risk_flags.append("fallback_data_present")

        return MarketConfidenceScore(
            confidence_score=confidence_score,
            source_reliability=source_reliability,
            evidence_sources=evidence_sources,
            real_data_ratio=real_data_ratio,
            risk_flags=sorted(set(risk_flags)),
        )

    def evaluate_reality(self, signals: dict[str, dict]) -> MarketConfidenceScore:
        source_reliability: dict[str, float] = {}
        evidence_sources: list[dict[str, Any]] = []
        coverage_numerator = 0.0
        coverage_denominator = 0.0
        active_values: list[float] = []
        freshness_values: list[float] = []
        active_confidences: list[float] = []
        active_trends: list[str] = []

        for source, payload in signals.items():
            source_weight = float(self.SOURCE_WEIGHTS.get(source, 0.5))
            status = str(payload.get("data_status") or "fallback").lower()
            status_weight = float(self.STATUS_WEIGHTS.get(status, 0.2))
            confidence = max(0.0, min(1.0, float(payload.get("confidence") or 0)))
            signal_strength = max(0.0, min(100.0, float(payload.get("value") or 0)))
            reliability = round(source_weight * status_weight * confidence, 4)

            include_in_coverage = source in self.CORE_REALITY_SOURCES or status in {"real", "limited", "partial"} or signal_strength > 0
            if include_in_coverage:
                coverage_denominator += source_weight
                coverage_numerator += source_weight * status_weight
            if status in {"real", "limited"} and signal_strength > 0:
                active_values.append(signal_strength)
                active_confidences.append(confidence)
                active_trends.append(str(payload.get("trend") or "flat"))
            freshness_values.append(confidence)
            source_reliability[source] = reliability
            evidence_sources.append(
                {
                    "source": source,
                    "status": status,
                    "reliability": reliability,
                    "signal_strength": round(signal_strength, 2),
                    "confidence": round(confidence, 4),
                    "timestamp": str(payload.get("timestamp") or ""),
                }
            )

        real_data_ratio = round(max(0.0, min(1.0, coverage_numerator / coverage_denominator if coverage_denominator else 0.0)), 4)
        if len(active_values) >= 2:
            average_value = mean(active_values)
            deviation = pstdev(active_values) if len(active_values) > 1 else 0.0
            variation_ratio = deviation / average_value if average_value > 0 else 1.0
            trend_up_ratio = active_trends.count("up") / len(active_trends) if active_trends else 0.0
            value_consistency = max(0.0, min(1.0, 1 - (variation_ratio / 1.2)))
            trend_consistency = max(0.0, min(1.0, 0.45 + trend_up_ratio * 0.55))
            consistency = round((value_consistency * 0.65) + (trend_consistency * 0.35), 4)
        else:
            consistency = 0.45
        freshness = (
            sum(active_confidences) / len(active_confidences)
            if active_confidences
            else (sum(freshness_values) / len(freshness_values) if freshness_values else 0.0)
        )
        confidence_score = round(
            max(
                0.0,
                min(
                    1.0,
                    real_data_ratio * 0.55
                    + consistency * 0.25
                    + freshness * 0.2,
                ),
            ),
            4,
        )

        risk_flags: list[str] = []
        if confidence_score < 0.6:
            risk_flags.append("low_market_confidence")
        if real_data_ratio < 0.55:
            risk_flags.append("low_real_ratio")
        if any(item.get("status") == "fallback" for item in evidence_sources):
            risk_flags.append("fallback_data_present")
        for source in sorted(self.CORE_REALITY_SOURCES):
            if str((signals.get(source) or {}).get("data_status") or "fallback") == "fallback":
                risk_flags.append(f"{source}_fallback")
        return MarketConfidenceScore(
            confidence_score=confidence_score,
            source_reliability=source_reliability,
            evidence_sources=evidence_sources,
            real_data_ratio=real_data_ratio,
            risk_flags=sorted(set(risk_flags)),
        )

    def shopify_commercial_signal(
        self,
        *,
        sales_validation: float,
        conversion_signal: float,
        repeat_purchase_signal: float,
        country_validation: float,
    ) -> dict:
        weighted = (
            float(sales_validation or 0) * 1.0
            + float(conversion_signal or 0) * 1.0
            + float(repeat_purchase_signal or 0) * 1.0
            + float(country_validation or 0) * 1.0
        ) / 4
        return {
            "sales_validation": round(float(sales_validation or 0), 2),
            "conversion_signal": round(float(conversion_signal or 0), 2),
            "repeat_purchase_signal": round(float(repeat_purchase_signal or 0), 2),
            "country_validation": round(float(country_validation or 0), 2),
            "shopify_commercial_signal": round(weighted, 2),
        }


market_confidence_engine = MarketConfidenceEngine()
