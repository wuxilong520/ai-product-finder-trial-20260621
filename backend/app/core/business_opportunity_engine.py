from __future__ import annotations


class BusinessOpportunityEngine:
    def evaluate(
        self,
        *,
        market_score: float,
        market_reality_score: float | None = None,
        amazon_demand: float,
        supplier_quality: float,
        profit_margin: float,
        market_confidence: float,
        market_confidence_score: float | None = None,
        amazon_confidence: float,
        supplier_confidence: float,
        profit_confidence: float,
        statuses: dict[str, str] | None = None,
        supply_score: float | None = None,
        profit_score: float | None = None,
        commercial_reality_score: float | None = None,
        purchase_signal: float | None = None,
        commercial_score: float | None = None,
    ) -> dict:
        normalized_market_score = float(market_reality_score if market_reality_score is not None else market_score or 0)
        normalized_profit_margin = float(profit_margin or 0)
        if normalized_profit_margin <= 1:
            normalized_profit_margin *= 100
        normalized_market_confidence = float(market_confidence_score if market_confidence_score is not None else market_confidence or 0)
        confidence_bonus = normalized_market_confidence * 100 * 0.1
        computed_supply_score = float(supply_score if supply_score is not None else supplier_quality or 0)
        computed_profit_score = float(profit_score if profit_score is not None else normalized_profit_margin or 0)
        normalized_purchase_signal = float(purchase_signal or 0)
        normalized_commercial_score = float(commercial_score if commercial_score is not None else commercial_reality_score or 0)
        commercial_reality_bonus = normalized_commercial_score * 0.08 + normalized_purchase_signal * 0.07
        competition_penalty = max(0.0, 100.0 - float(amazon_demand or 0)) * 0.15
        opportunity_score = round(
            max(
                0.0,
                min(
                    100.0,
                    normalized_market_score * 0.3
                    + computed_supply_score * 0.25
                    + computed_profit_score * 0.3
                    + float(amazon_demand or 0) * 0.15
                    + confidence_bonus
                    + commercial_reality_bonus
                    - competition_penalty,
                ),
            ),
            2,
        )
        if opportunity_score >= 75:
            recommendation = "BUY"
        elif opportunity_score >= 55:
            recommendation = "TEST"
        elif opportunity_score >= 35:
            recommendation = "WATCH"
        else:
            recommendation = "IGNORE"
        confidence = round(
            max(
                0.0,
                min(
                    1.0,
                    normalized_market_confidence * 0.35
                    + float(amazon_confidence or 0) * 0.25
                    + float(supplier_confidence or 0) * 0.2
                    + float(profit_confidence or 0) * 0.2,
                ),
            ),
            4,
        )
        if normalized_market_confidence < 0.6:
            recommendation = "WATCH" if recommendation in {"BUY", "TEST"} else recommendation
        elif normalized_market_confidence < 0.8 and recommendation == "BUY":
            recommendation = "TEST"
        risk_flags: list[str] = []
        statuses = statuses or {}
        if normalized_market_score < 40:
            risk_flags.append("low_market_score")
        if float(amazon_demand or 0) < 35:
            risk_flags.append("weak_amazon_demand")
        if float(supplier_quality or 0) < 60:
            risk_flags.append("low_supplier_quality")
        if float(normalized_profit_margin or 0) < 20:
            risk_flags.append("low_profit_margin")
        if confidence < 0.6:
            risk_flags.append("low_confidence")
        if any(status == "cached" for status in statuses.values()):
            risk_flags.append("cached_data_used")
        if any(status == "unavailable" for status in statuses.values()):
            risk_flags.append("source_unavailable")
        return {
            "market_score": round(normalized_market_score, 2),
            "amazon_score": round(float(amazon_demand or 0), 2),
            "supplier_score": round(float(supplier_quality or 0), 2),
            "profit_margin": round(float(normalized_profit_margin or 0), 2),
            "opportunity_score": opportunity_score,
            "recommendation": recommendation,
            "confidence": confidence,
            "confidence_bonus": round(confidence_bonus, 2),
            "commercial_reality_bonus": round(commercial_reality_bonus, 2),
            "purchase_signal": round(normalized_purchase_signal, 2),
            "commercial_score": round(normalized_commercial_score, 2),
            "risk_flags": sorted(set(risk_flags)),
        }


business_opportunity_engine = BusinessOpportunityEngine()
