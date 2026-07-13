from __future__ import annotations

from statistics import mean


class CompetitionPressureEngine:
    def score(
        self,
        *,
        amazon_signal: float,
        ebay_signal: float,
        walmart_signal: float,
        result_count_proxy: float = 0.0,
        brand_count: float = 0.0,
    ) -> float:
        platform_pressure = mean(
            [
                float(amazon_signal or 0),
                float(ebay_signal or 0),
                float(walmart_signal or 0),
            ]
        )
        search_pressure = min(100.0, float(result_count_proxy or 0) * 2.2)
        brand_pressure = min(100.0, float(brand_count or 0) * 4.5)
        score = platform_pressure * 0.5 + search_pressure * 0.25 + brand_pressure * 0.25
        return round(max(0.0, min(100.0, score)), 2)


competition_pressure_engine = CompetitionPressureEngine()
