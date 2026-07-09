from __future__ import annotations

from statistics import mean

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.repositories.market_analysis_history import market_analysis_history_repository


class MarketSignal(BaseModel):
    source: str
    signal_type: str
    value: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    is_real: bool


class MarketSignalEngine:
    def build(
        self,
        *,
        keyword: str,
        region: str,
        data_sources: dict[str, dict],
        market_intelligence: dict,
        db: Session | None = None,
    ) -> dict:
        signals: list[MarketSignal] = []
        source_status: dict[str, str] = {}
        source_confidences: list[float] = []
        mock_sources = 0

        for source_name, payload in data_sources.items():
            data = payload.get("data") or {}
            confidence = float(payload.get("confidence") or 0)
            is_real = not bool(payload.get("is_mock"))
            source_status[source_name] = str(payload.get("source_status") or ("real" if is_real else "mock"))
            source_confidences.append(confidence)
            if not is_real:
                mock_sources += 1

            if source_name == "google":
                signals.extend([
                    MarketSignal(source="google", signal_type="demand", value=self._score(data.get("trend_value", data.get("trend_score"))), confidence=confidence, is_real=is_real),
                    MarketSignal(source="google", signal_type="trend", value=self._score(data.get("trend_value", data.get("trend_score"))), confidence=confidence, is_real=is_real),
                    MarketSignal(source="google", signal_type="category_growth", value=self._score(50 + float(data.get("growth_rate") or 0)), confidence=confidence, is_real=is_real),
                ])
            elif source_name == "amazon":
                signals.extend([
                    MarketSignal(source="amazon", signal_type="demand", value=self._score(data.get("demand_indicator", data.get("market_signal"))), confidence=confidence, is_real=is_real),
                    MarketSignal(source="amazon", signal_type="competition", value=self._score(data.get("competition_indicator", 0)), confidence=confidence, is_real=is_real),
                    MarketSignal(source="amazon", signal_type="category_growth", value=self._score(data.get("category_strength", data.get("market_signal"))), confidence=confidence, is_real=is_real),
                ])
            elif source_name == "tiktok":
                signals.extend([
                    MarketSignal(source="tiktok", signal_type="demand", value=self._score(data.get("viral_score")), confidence=confidence, is_real=is_real),
                    MarketSignal(source="tiktok", signal_type="trend", value=self._score(50 + float(data.get("growth_rate", data.get("content_growth")) or 0)), confidence=confidence, is_real=is_real),
                ])
            elif source_name == "shopify":
                signals.extend([
                    MarketSignal(source="shopify", signal_type="demand", value=self._score(data.get("category_activity")), confidence=confidence, is_real=is_real),
                    MarketSignal(source="shopify", signal_type="competition", value=self._score(min(100, float(data.get("product_count") or 0) * 4 + float(data.get("active_product_ratio") or 0) * 0.4)), confidence=confidence, is_real=is_real),
                    MarketSignal(source="shopify", signal_type="category_growth", value=self._score(data.get("growth_signal")), confidence=confidence, is_real=is_real),
                ])

        demand_signals = [item.value for item in signals if item.signal_type == "demand"]
        trend_signals = [item.value for item in signals if item.signal_type in {"trend", "category_growth"}]
        competition_signals = [item.value for item in signals if item.signal_type == "competition"]

        previous_record = None
        if db is not None:
            previous_record = market_analysis_history_repository.latest_for_keyword(
                db,
                keyword=keyword,
                region=region,
            )

        demand_score = round(mean(demand_signals), 2) if demand_signals else float(market_intelligence.get("demand_score") or 0)
        trend_score = round(mean(trend_signals), 2) if trend_signals else float(market_intelligence.get("trend_strength") or 0)
        competition_score = round(mean(competition_signals), 2) if competition_signals else float(market_intelligence.get("market_saturation") or 0)
        market_growth = round(float(((data_sources.get("google") or {}).get("data") or {}).get("growth_rate") or 0), 2)
        trend_direction = self._trend_direction(
            market_growth=market_growth,
            previous_score=float(previous_record.score) if previous_record else None,
            current_score=float(market_intelligence.get("demand_score") or 0),
        )
        overall_confidence = round(mean(source_confidences), 4) if source_confidences else 0.0
        all_mock = mock_sources == len(data_sources) if data_sources else True
        if all_mock:
            overall_confidence = min(overall_confidence, 0.3)

        return {
            "market_signals": [item.model_dump(mode="json") for item in signals],
            "source_status": source_status,
            "demand_score": round(self._score(demand_score), 2),
            "trend_score": round(self._score(trend_score), 2),
            "competition_score": round(self._score(competition_score), 2),
            "market_growth": market_growth,
            "trend_direction": trend_direction,
            "confidence": overall_confidence,
            "all_mock": all_mock,
            "previous_record": previous_record,
        }

    def _trend_direction(self, *, market_growth: float, previous_score: float | None, current_score: float) -> str:
        if previous_score is not None:
            delta = current_score - previous_score
            if delta > 5:
                return "up"
            if delta < -5:
                return "down"
        if market_growth > 3:
            return "up"
        if market_growth < -3:
            return "down"
        return "flat"

    def _score(self, value: float | int | None) -> float:
        try:
            return max(0.0, min(100.0, float(value or 0)))
        except (TypeError, ValueError):
            return 0.0


market_signal_engine = MarketSignalEngine()
