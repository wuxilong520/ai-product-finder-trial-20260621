from __future__ import annotations


class OpportunityScoringEngine:
    def score(
        self,
        *,
        market_score: float,
        supplier_score: float,
        profit_score: float,
        competition_score: float,
    ) -> dict:
        market_component = float(market_score or 0) * 0.30
        supply_component = float(supplier_score or 0) * 0.25
        profit_component = float(profit_score or 0) * 0.30
        competition_penalty = float(competition_score or 0) * 0.15
        total = round(max(0.0, min(100.0, market_component + supply_component + profit_component - competition_penalty)), 2)
        if total >= 75:
            recommendation = "BUY"
        elif total >= 55:
            recommendation = "TEST"
        elif total >= 35:
            recommendation = "WATCH"
        else:
            recommendation = "IGNORE"
        risk_flags: list[str] = []
        if float(market_score or 0) < 40:
            risk_flags.append("low_market_score")
        if float(supplier_score or 0) < 60:
            risk_flags.append("weak_supplier_score")
        if float(profit_score or 0) < 20:
            risk_flags.append("low_profit_margin")
        if float(competition_score or 0) > 70:
            risk_flags.append("high_competition")
        return {
            "score": total,
            "recommendation": recommendation,
            "components": {
                "market_component": round(market_component, 2),
                "supply_component": round(supply_component, 2),
                "profit_component": round(profit_component, 2),
                "competition_penalty": round(competition_penalty, 2),
            },
            "risk_flags": risk_flags,
        }


opportunity_scoring_engine = OpportunityScoringEngine()
