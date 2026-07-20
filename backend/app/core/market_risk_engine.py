from __future__ import annotations


class MarketRiskEngine:
    def evaluate(
        self,
        *,
        market_score: float,
        real_data_ratio: float,
        competition_score: float,
        trend_score: float,
        historical_score: float,
    ) -> list[str]:
        flags: list[str] = []
        if float(market_score or 0) < 35 or float(real_data_ratio or 0) < 0.6:
            flags.append("insufficient_data")
        if float(competition_score or 0) >= 70:
            flags.append("competition_spike")
        if float(trend_score or 0) <= 25:
            flags.append("demand_drop")
        if float(trend_score or 0) >= 85 and float(real_data_ratio or 0) < 0.8:
            flags.append("trend_fake")
        if historical_score and float(market_score or 0) < historical_score * 0.7:
            flags.append("seasonal_risk")
        return sorted(set(flags))


market_risk_engine = MarketRiskEngine()
