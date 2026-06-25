from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.repositories.business_truth_decision import business_truth_decision_repository
from app.repositories.product import product_repository
from app.services.cost_model.product_cost_engine import product_cost_engine
from app.services.decision_engine import decision_engine
from app.services.market_intelligence_engine import market_intelligence_engine
from app.services.market_truth_layer.external_price_calibrator import external_price_calibrator
from app.services.profit_real_engine import profit_real_engine
from app.services.supplier_matching_engine import supplier_matching_engine


class DecisionTruthWrapper:
    def recommend(self, db: Session, product_id: int) -> dict:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise AppError("PRODUCT_NOT_FOUND", "商品不存在", "db", 404)

        base_decision = decision_engine.recommend(db, product_id)
        keyword = product.title_zh or product.title
        market_payload = market_intelligence_engine.analyze_keyword(db, keyword)
        suppliers_payload = supplier_matching_engine.match(db, keyword)

        selling_price = float(product.current_price or 0)
        calibrated_market = external_price_calibrator.calibrate(
            keyword=keyword,
            product_title=product.title,
            current_price=selling_price,
            market_payload=market_payload,
        )
        cost_payload = product_cost_engine.calculate(
            suppliers=suppliers_payload["suppliers"],
            selling_price=selling_price,
        )
        profit_payload = profit_real_engine.calculate(
            selling_price=selling_price,
            total_cost=float(cost_payload["total_cost"]),
        )

        truth_score = self._truth_score(
            phase4_final_score=float(base_decision["final_score"]),
            profit_margin=float(profit_payload["profit_margin"]),
            demand_signal=calibrated_market["demand_signal"],
            simulated_penalty_count=len(set(cost_payload["simulated_dependencies"] + calibrated_market["simulated_dependencies"])),
        )
        truth_recommendation, truth_level = self._truth_recommendation(
            truth_score=truth_score,
            profit_margin=float(profit_payload["profit_margin"]),
        )

        reasons = self._build_reasons(
            base_decision=base_decision,
            cost_payload=cost_payload,
            profit_payload=profit_payload,
            calibrated_market=calibrated_market,
            truth_score=truth_score,
            truth_recommendation=truth_recommendation,
        )

        merged_dependencies = list(dict.fromkeys(cost_payload["simulated_dependencies"] + calibrated_market["simulated_dependencies"]))
        payload = {
            "keyword": keyword,
            "selling_price": round(selling_price, 2),
            "real_market_price": round(float(calibrated_market["real_market_price"]), 2),
            "market_price_min": round(float(calibrated_market["price_range"]["min"]), 2),
            "market_price_max": round(float(calibrated_market["price_range"]["max"]), 2),
            "demand_signal": calibrated_market["demand_signal"],
            "supplier_cost": round(float(cost_payload["cost_breakdown"]["supplier_cost"]), 2),
            "shipping_cost": round(float(cost_payload["cost_breakdown"]["shipping_cost"]), 2),
            "platform_fee": round(float(cost_payload["cost_breakdown"]["platform_fee"]), 2),
            "packaging_cost": round(float(cost_payload["cost_breakdown"]["packaging_cost"]), 2),
            "exchange_rate": round(float(cost_payload["cost_breakdown"]["exchange_rate"]), 4),
            "total_cost": round(float(cost_payload["total_cost"]), 2),
            "profit": round(float(profit_payload["profit"]), 2),
            "profit_margin": round(float(profit_payload["profit_margin"]), 4),
            "break_even_price": round(float(profit_payload["break_even_price"]), 2),
            "phase4_final_score": round(float(base_decision["final_score"]), 2),
            "truth_score": round(float(truth_score), 2),
            "truth_recommendation": truth_recommendation,
            "truth_level": truth_level,
            "still_uses_simulated_data": True,
            "simulated_dependencies": merged_dependencies,
            "cost_breakdown": cost_payload["cost_breakdown"],
            "external_market_snapshot": calibrated_market,
            "reasons": reasons,
        }
        business_truth_decision_repository.upsert(db, product_id=product_id, **payload)
        return payload

    def _truth_score(
        self,
        *,
        phase4_final_score: float,
        profit_margin: float,
        demand_signal: str,
        simulated_penalty_count: int,
    ) -> float:
        demand_bonus = 10 if demand_signal == "strong" else 4 if demand_signal == "medium" else -6
        profit_bonus = max(min(profit_margin * 100, 20), -20)
        penalty = min(simulated_penalty_count * 3.5, 18)
        score = phase4_final_score * 0.6 + 25 + profit_bonus + demand_bonus - penalty
        return max(0.0, min(100.0, score))

    def _truth_recommendation(self, *, truth_score: float, profit_margin: float) -> tuple[str, str]:
        if truth_score >= 80 and profit_margin >= 0.25:
            return "真实商业推荐", "A"
        if truth_score >= 60 and profit_margin >= 0.12:
            return "可继续核算", "B"
        if truth_score >= 45:
            return "仅适合人工复核", "C"
        return "不建议投入", "D"

    def _build_reasons(
        self,
        *,
        base_decision: dict,
        cost_payload: dict,
        profit_payload: dict,
        calibrated_market: dict,
        truth_score: float,
        truth_recommendation: str,
    ) -> list[str]:
        return [
            f"原 Phase 4 决策评分为 {float(base_decision['final_score']):.2f}，本次保持原系统不变，只在后面叠加真实性校准。",
            f"按真实性成本模型估算，总成本约 {float(cost_payload['total_cost']):.2f}，其中供货成本约 {float(cost_payload['cost_breakdown']['supplier_cost']):.2f}。",
            f"按当前售价测算，真实利润约 {float(profit_payload['profit']):.2f}，利润率约 {float(profit_payload['profit_margin']) * 100:.2f}%。",
            f"外部市场校准后，影子市场价约 {float(calibrated_market['real_market_price']):.2f}，需求信号为 {calibrated_market['demand_signal']}。",
            f"真实性增强后评分为 {truth_score:.2f}，商业推荐结论为：{truth_recommendation}。",
            "当前仍未接入真实 Amazon / Shopee / TikTok API，外部市场价格仍属于规则校准结果。",
            "当前供应链成本仍依赖搜索入口参考价，而不是工厂实时报价或真实成交价。",
        ][:7]


decision_truth_wrapper = DecisionTruthWrapper()
