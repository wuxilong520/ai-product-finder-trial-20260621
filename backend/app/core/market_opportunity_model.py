from __future__ import annotations

from pydantic import BaseModel, Field


class MarketOpportunity(BaseModel):
    score: float = Field(..., ge=0, le=100)
    level: str
    recommendation: str
    supply_accessibility: float = Field(..., ge=0, le=100)


class MarketOpportunityModel:
    def evaluate(
        self,
        *,
        demand_score: float,
        trend_score: float,
        competition_score: float,
        platform_compatibility: dict | None = None,
    ) -> MarketOpportunity:
        compatibility = platform_compatibility or {}
        supply_accessibility = self._supply_accessibility(compatibility)
        score = (
            float(demand_score) * 0.40
            + float(trend_score) * 0.25
            + max(0.0, 100.0 - float(competition_score)) * 0.20
            + float(supply_accessibility) * 0.15
        )
        normalized_score = round(max(0.0, min(100.0, score)), 2)
        if normalized_score >= 80:
            level = "HIGH"
            recommendation = "BUY"
        elif normalized_score >= 60:
            level = "MEDIUM"
            recommendation = "TEST"
        else:
            level = "LOW"
            recommendation = "IGNORE"
        return MarketOpportunity(
            score=normalized_score,
            level=level,
            recommendation=recommendation,
            supply_accessibility=round(supply_accessibility, 2),
        )

    def _supply_accessibility(self, compatibility: dict) -> float:
        alibaba_matches = compatibility.get("alibaba_match") or []
        shopify_ready = bool(compatibility.get("shopify_ready"))
        tiktok_potential = float(compatibility.get("tiktok_potential") or 0)
        base = min(100.0, len(alibaba_matches) * 18 + (25 if shopify_ready else 0) + tiktok_potential * 0.25)
        return max(0.0, min(100.0, base))


market_opportunity_model = MarketOpportunityModel()
