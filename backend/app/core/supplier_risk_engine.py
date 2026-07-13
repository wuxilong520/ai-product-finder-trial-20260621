from __future__ import annotations


class SupplierRiskEngine:
    def evaluate(
        self,
        *,
        authenticity_score: float,
        price_score: float,
        moq_score: float,
        stability_score: float,
        has_history: bool,
        missing_fields: list[str],
        price_ratio: float | None,
    ) -> dict:
        risk_flags: list[str] = []
        risk_score = 0.0

        if missing_fields:
            risk_score += min(30.0, len(missing_fields) * 6.0)
            risk_flags.append("信息缺失")
        if authenticity_score < 50:
            risk_score += 20.0
            risk_flags.append("真实性偏弱")
        if price_ratio is not None and price_ratio < 0.65:
            risk_score += 18.0
            risk_flags.append("价格异常偏低")
        elif price_ratio is not None and price_ratio > 1.25:
            risk_score += 12.0
            risk_flags.append("价格偏高")
        if moq_score < 45:
            risk_score += 12.0
            risk_flags.append("MOQ异常")
        if stability_score < 45:
            risk_score += 14.0
            risk_flags.append("供应不稳定")
        if price_score < 40:
            risk_score += 10.0
            risk_flags.append("成本竞争力弱")
        if not has_history:
            risk_score += 10.0
            risk_flags.append("无历史记录")

        risk_score = round(max(0.0, min(100.0, risk_score)), 2)
        if risk_score >= 60:
            level = "HIGH"
        elif risk_score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"
        return {
            "supplier_risk_score": risk_score,
            "risk_level": level,
            "risk_flags": risk_flags,
        }


supplier_risk_engine = SupplierRiskEngine()
