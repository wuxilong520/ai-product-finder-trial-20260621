from __future__ import annotations

from statistics import mean


class MarketOpportunityScore:
    def score(
        self,
        *,
        amazon_score: float,
        tiktok_score: float,
        meta_score: float,
        seo_score: float,
        shopify_score: float,
        historical_score: float,
    ) -> float:
        return round(
            max(
                0.0,
                min(
                    100.0,
                    float(amazon_score or 0) * 0.25
                    + float(tiktok_score or 0) * 0.20
                    + float(meta_score or 0) * 0.15
                    + float(seo_score or 0) * 0.15
                    + float(shopify_score or 0) * 0.15
                    + float(historical_score or 0) * 0.10,
                ),
            ),
            2,
        )

    def historical_score(self, previous_scores: list[float]) -> float:
        valid_scores = [float(item or 0) for item in previous_scores if item is not None]
        return round(mean(valid_scores), 2) if valid_scores else 0.0


market_opportunity_score = MarketOpportunityScore()
