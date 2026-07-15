from __future__ import annotations

from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.procurement import ProcurementAnalysisHistory, ProcurementPoolItem, ProcurementSupplierItem
from app.services.market_intelligence_engine import market_intelligence_engine
from app.services.profit_truth_engine import profit_truth_engine


class ProcurementAnalysisEngine:
    def analyze(self, db: Session, *, pool_item: ProcurementPoolItem, supplier_items: list[ProcurementSupplierItem]) -> dict:
        market = market_intelligence_engine.analyze_keyword(
            db,
            keyword=pool_item.keyword,
            region="US",
            category=pool_item.category,
            user_id=pool_item.user_id,
        )
        supplier_score = max((float(item.supplier_truth_score or item.supplier_score or 0) for item in supplier_items), default=0.0)
        avg_risk = mean([float(item.risk_score or 0) for item in supplier_items]) if supplier_items else 100.0
        best_price = min((float(item.price or 0) for item in supplier_items if float(item.price or 0) > 0), default=float(pool_item.min_price or 0))
        estimated_sell_price = round(max(best_price * 2.15, best_price + 14, float(pool_item.avg_price or 0) * 1.8, 29.9), 2) if best_price > 0 else 39.9
        shipping_cost = round(max(6.5, best_price * 0.16), 2)
        platform_fee = round(estimated_sell_price * 0.12, 2)
        ad_cost = round(estimated_sell_price * 0.08, 2)
        profit = profit_truth_engine.calculate(
            selling_price=estimated_sell_price,
            platform_fee=platform_fee,
            shipping_cost=shipping_cost,
            ad_cost=ad_cost,
            product_cost=best_price,
            currency_loss=0.0,
        )
        profit_score = round(max(0.0, min(100.0, float(profit.get("margin_rate") or 0) * 100 * 2.2)), 2)
        market_score = float(market.get("market_score") or market.get("recommendation_score") or 0)
        competition = float(market.get("competition_score") or 0)
        risk_score = round(max(0.0, min(100.0, avg_risk * 0.55 + competition * 0.45)), 2)
        risk_level = "low" if risk_score < 35 else "medium" if risk_score < 65 else "high"
        product_score = round(
            max(
                0.0,
                min(
                    100.0,
                    market_score * 0.3
                    + supplier_score * 0.3
                    + profit_score * 0.25
                    + max(0.0, 100.0 - risk_score) * 0.15,
                ),
            ),
            2,
        )
        if risk_level == "high":
            recommendation = "不建议"
        elif product_score >= 78:
            recommendation = "建议采购"
        elif product_score >= 60:
            recommendation = "测试销售"
        elif product_score >= 45:
            recommendation = "谨慎观察"
        else:
            recommendation = "不建议"
        reason = [
            f"市场分 {market_score:.1f}",
            f"供应商分 {supplier_score:.1f}",
            f"利润分 {profit_score:.1f}",
            f"风险等级 {risk_level}",
        ]
        snapshot = {
            "product_score": product_score,
            "market_score": market_score,
            "supplier_score": round(supplier_score, 2),
            "profit_score": profit_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "reason": reason,
            "profit": profit,
            "market": market,
        }
        db.add(
            ProcurementAnalysisHistory(
                pool_item_id=pool_item.id,
                product_score=product_score,
                market_score=market_score,
                supplier_score=round(supplier_score, 2),
                profit_score=profit_score,
                risk_level=risk_level,
                recommendation=recommendation,
                reason=reason,
                snapshot=snapshot,
            )
        )
        pool_item.market_score = market_score
        pool_item.estimated_profit = round(float(profit.get("net_profit") or 0), 2)
        pool_item.status = "ANALYZED"
        db.add(pool_item)
        db.commit()
        return snapshot

    def latest_for_pool_item(self, db: Session, *, pool_item_id: int) -> ProcurementAnalysisHistory | None:
        return db.scalar(
            select(ProcurementAnalysisHistory)
            .where(ProcurementAnalysisHistory.pool_item_id == pool_item_id)
            .order_by(ProcurementAnalysisHistory.created_at.desc())
        )


procurement_analysis_engine = ProcurementAnalysisEngine()
