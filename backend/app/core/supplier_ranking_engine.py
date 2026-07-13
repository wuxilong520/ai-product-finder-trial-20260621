from __future__ import annotations


class SupplierRankingEngine:
    def rank(self, reports: list[dict]) -> list[dict]:
        ranked = []
        for item in reports:
            real_score = float(item.get("supplier_real_score") or 0)
            risk_score = float(item.get("supplier_risk_score") or 0)
            profit_contribution = float(item.get("profit_contribution") or 0)
            ranking_score = round(
                max(
                    0.0,
                    min(
                        100.0,
                        real_score * 0.65
                        + max(0.0, 100.0 - risk_score) * 0.2
                        + profit_contribution * 0.15,
                    ),
                ),
                2,
            )
            ranked.append({**item, "ranking_score": ranking_score})
        return sorted(
            ranked,
            key=lambda item: (
                -float(item.get("ranking_score") or 0),
                -float(item.get("supplier_real_score") or 0),
                float(item.get("supplier_risk_score") or 999),
            ),
        )


supplier_ranking_engine = SupplierRankingEngine()
