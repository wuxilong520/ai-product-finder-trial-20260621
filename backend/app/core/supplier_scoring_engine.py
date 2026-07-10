from __future__ import annotations


class SupplierScoringEngine:
    def quality_score(
        self,
        *,
        factory_score: float,
        price_advantage: float,
        delivery_score: float,
        verification_score: float,
    ) -> dict:
        score = round(
            float(factory_score or 0) * 0.3
            + float(price_advantage or 0) * 0.25
            + float(delivery_score or 0) * 0.2
            + float(verification_score or 0) * 0.25,
            2,
        )
        if score >= 85:
            level = "A"
            recommendation = "recommended"
        elif score >= 70:
            level = "B"
            recommendation = "test"
        elif score >= 55:
            level = "C"
            recommendation = "watch"
        else:
            level = "D"
            recommendation = "not_recommended"
        reasons: list[str] = []
        if float(factory_score or 0) >= 75:
            reasons.append("工厂能力较强")
        if float(price_advantage or 0) >= 75:
            reasons.append("价格优势明显")
        if float(delivery_score or 0) < 45:
            reasons.append("交付能力偏弱")
        if float(verification_score or 0) < 50:
            reasons.append("认证或校验不足")
        return {
            "score": score,
            "supplier_score": score,
            "level": level,
            "recommendation": recommendation,
            "reason": reasons or ["供应链信息基本完整，可进入下一步判断。"],
        }

    def score(
        self,
        *,
        stability_score: float,
        price_competitiveness: float,
        moq_reasonableness: float,
        delivery_score: float,
        certification_score: float,
        feedback_score: float,
    ) -> dict:
        reasons: list[str] = []
        supplier_score = round(
            stability_score * 0.22
            + price_competitiveness * 0.22
            + moq_reasonableness * 0.18
            + delivery_score * 0.14
            + certification_score * 0.12
            + feedback_score * 0.12,
            2,
        )
        if stability_score >= 75:
            reasons.append("供应稳定性较好")
        elif stability_score < 45:
            reasons.append("供应稳定性偏弱")
        if price_competitiveness >= 75:
            reasons.append("价格竞争力较好")
        elif price_competitiveness < 45:
            reasons.append("进货价偏高")
        if moq_reasonableness < 45:
            reasons.append("MOQ 偏高")
        if delivery_score < 45:
            reasons.append("交付时效偏弱")
        if certification_score >= 70:
            reasons.append("认证信息较完整")
        elif certification_score <= 20:
            reasons.append("缺少认证信息")
        if feedback_score >= 70:
            reasons.append("历史反馈较好")
        if supplier_score >= 85:
            level = "A"
            recommendation = "recommended"
        elif supplier_score >= 70:
            level = "B"
            recommendation = "test"
        elif supplier_score >= 55:
            level = "C"
            recommendation = "watch"
        else:
            level = "D"
            recommendation = "not_recommended"
        return {
            "score": supplier_score,
            "supplier_score": supplier_score,
            "level": level,
            "recommendation": recommendation,
            "reason": reasons or ["当前供应数据较少，先观察。"],
        }

    def moq_reasonableness(self, *, moq: int, quantity: int) -> float:
        if quantity <= 0:
            return 20.0
        ratio = moq / quantity
        if ratio <= 0.2:
            return 92.0
        if ratio <= 0.5:
            return 75.0
        if ratio <= 1:
            return 50.0
        return 20.0

    def delivery_score(self, *, delivery_time_days: int | None) -> float:
        if delivery_time_days is None or delivery_time_days <= 0:
            return 40.0
        if delivery_time_days <= 3:
            return 92.0
        if delivery_time_days <= 7:
            return 78.0
        if delivery_time_days <= 15:
            return 60.0
        return 35.0

    def certification_score(self, *, certification: str | None) -> float:
        text = str(certification or "").strip().lower()
        if not text:
            return 20.0
        if any(token in text for token in ["iso", "质检", "认证", "ce", "fcc", "rohs"]):
            return 88.0
        return 55.0

    def stability_score(
        self,
        *,
        factory_score: float,
        transaction_history: float,
        source_confidence: float,
    ) -> float:
        return round(
            factory_score * 0.4
            + transaction_history * 0.35
            + max(0.0, min(100.0, source_confidence * 100)) * 0.25,
            2,
        )

    def feedback_score(self, *, trust_score: float, feedback_status: str | None) -> float:
        base = float(trust_score or 0)
        status = str(feedback_status or "").lower()
        if "good" in status or "success" in status:
            base += 10
        if "bad" in status or "refund" in status or "failed" in status:
            base -= 15
        return max(0.0, min(100.0, round(base, 2)))

    def price_competitiveness(self, *, price_mid: float, expected_price: float | None) -> float:
        if not expected_price or expected_price <= 0:
            return 60.0
        ratio = price_mid / expected_price
        if ratio <= 0.25:
            return 95.0
        if ratio <= 0.4:
            return 82.0
        if ratio <= 0.55:
            return 68.0
        if ratio <= 0.7:
            return 52.0
        return 28.0


supplier_scoring_engine = SupplierScoringEngine()
