from __future__ import annotations


class BusinessOpportunityEngine:
    def evaluate(
        self,
        *,
        market_score: float,
        amazon_demand: float,
        supplier_quality: float,
        profit_margin: float,
        market_confidence: float,
        amazon_confidence: float,
        supplier_confidence: float,
        profit_confidence: float,
        statuses: dict[str, str] | None = None,
    ) -> dict:
        normalized_profit_margin = float(profit_margin or 0)
        if normalized_profit_margin <= 1:
            normalized_profit_margin *= 100
        opportunity_score = round(
            max(
                0.0,
                min(
                    100.0,
                    float(market_score or 0) * 0.45
                    + float(amazon_demand or 0) * 0.25
                    + float(supplier_quality or 0) * 0.15
                    + float(normalized_profit_margin or 0) * 0.15,
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
                    float(market_confidence or 0) * 0.35
                    + float(amazon_confidence or 0) * 0.25
                    + float(supplier_confidence or 0) * 0.2
                    + float(profit_confidence or 0) * 0.2,
                ),
            ),
            4,
        )
        risk_flags: list[str] = []
        statuses = statuses or {}
        if float(market_score or 0) < 40:
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
            "market_score": round(float(market_score or 0), 2),
            "amazon_score": round(float(amazon_demand or 0), 2),
            "supplier_score": round(float(supplier_quality or 0), 2),
            "profit_margin": round(float(normalized_profit_margin or 0), 2),
            "opportunity_score": opportunity_score,
            "recommendation": recommendation,
            "confidence": confidence,
            "risk_flags": sorted(set(risk_flags)),
        }


business_opportunity_engine = BusinessOpportunityEngine()
