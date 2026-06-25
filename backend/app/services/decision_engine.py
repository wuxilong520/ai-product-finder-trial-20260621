from __future__ import annotations

from statistics import mean

from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.models.product import Product
from app.repositories.decision_recommendation import decision_recommendation_repository
from app.repositories.product import product_repository
from app.services.market_intelligence_engine import market_intelligence_engine
from app.services.product_intelligence_engine import product_intelligence_engine
from app.services.supplier_matching_engine import supplier_matching_engine


class DecisionEngine:
    def recommend(self, db: Session, product_id: int) -> dict:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise AppError("PRODUCT_NOT_FOUND", "商品不存在", "db", 404)

        product_intelligence = product_intelligence_engine.get_or_create_intelligence(db, product_id)
        market_keyword = self._pick_market_keyword(product)
        market_intelligence = market_intelligence_engine.analyze_keyword(db, market_keyword)
        supplier_matches = supplier_matching_engine.match(db, market_keyword)

        intelligence_score = float(product_intelligence["recommendation_score"])
        market_score = float(market_intelligence["recommendation_score"])
        supplier_score = self._supplier_score(supplier_matches["suppliers"])
        profit_score = float(product_intelligence["profit_score"])
        risk_score = float(product_intelligence["risk_score"])

        final_score = self._clamp(
            0.30 * intelligence_score
            + 0.25 * market_score
            + 0.20 * supplier_score
            + 0.15 * profit_score
            - 0.10 * risk_score
        )

        recommendation, level = self._recommendation(final_score)
        reasons = self._build_reasons(
            product=product,
            intelligence_score=intelligence_score,
            market_score=market_score,
            supplier_score=supplier_score,
            profit_score=profit_score,
            risk_score=risk_score,
            final_score=final_score,
            top_supplier=supplier_matches["suppliers"][0] if supplier_matches["suppliers"] else None,
        )

        payload = {
            "intelligence_score": round(intelligence_score, 2),
            "market_score": round(market_score, 2),
            "supplier_score": round(supplier_score, 2),
            "profit_score": round(profit_score, 2),
            "risk_score": round(risk_score, 2),
            "final_score": round(final_score, 2),
            "recommendation": recommendation,
            "recommendation_level": level,
            "reasons": reasons,
        }
        decision_recommendation_repository.upsert(db, product_id=product_id, **payload)
        return payload

    def _pick_market_keyword(self, product: Product) -> str:
        if product.title_zh:
            return product.title_zh.split(" ")[0]
        return product.title.split(" ")[0] if product.title else f"product-{product.id}"

    def _supplier_score(self, suppliers: list[dict]) -> float:
        if not suppliers:
            return 0.0
        top_scores = [float(item["match_score"]) for item in suppliers[:3]]
        return self._clamp(mean(top_scores))

    def _recommendation(self, final_score: float) -> tuple[str, str]:
        if final_score >= 85:
            return "强烈推荐上架", "S"
        if final_score >= 70:
            return "推荐上架", "A"
        if final_score >= 50:
            return "继续观察", "B"
        return "不推荐", "C"

    def _build_reasons(
        self,
        *,
        product: Product,
        intelligence_score: float,
        market_score: float,
        supplier_score: float,
        profit_score: float,
        risk_score: float,
        final_score: float,
        top_supplier: dict | None,
    ) -> list[str]:
        reasons = [
            f"商品情报评分为 {intelligence_score:.1f}，说明商品本身基础质量与转化潜力处于 {'较好' if intelligence_score >= 70 else '中等' if intelligence_score >= 50 else '偏弱'} 区间。",
            f"市场评分为 {market_score:.1f}，当前关键词在现有商品库中的市场热度和需求表现{'不错' if market_score >= 70 else '一般' if market_score >= 50 else '偏弱'}。",
            f"供应链评分为 {supplier_score:.1f}，说明当前可用供应链匹配度{'较高' if supplier_score >= 70 else '一般' if supplier_score >= 50 else '不足'}。",
            f"利润评分为 {profit_score:.1f}，风险评分为 {risk_score:.1f}，利润和风险已经一起纳入最终决策。",
            f"最终决策评分为 {final_score:.1f}，当前建议为：{self._recommendation(final_score)[0]}。",
        ]
        if top_supplier:
            reasons.append(f"当前优先供应链来自 {top_supplier['platform']}，匹配度约 {float(top_supplier['match_score']):.1f}。")
        if product.title:
            reasons.append(f"本次决策对应商品：{product.title[:40]}")
        return reasons[:7]

    def _clamp(self, value: float) -> float:
        return max(0.0, min(100.0, value))


decision_engine = DecisionEngine()
