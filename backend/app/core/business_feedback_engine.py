from __future__ import annotations

from sqlalchemy.orm import Session

from app.adapters.execution.shopify_adapter import ShopifyExecutionAdapter
from app.core.feedback_loop_v2 import feedback_loop_v2
from app.repositories.business_opportunity_history import business_opportunity_history_repository


class BusinessFeedbackEngine:
    def __init__(self) -> None:
        self.shopify = ShopifyExecutionAdapter()

    def collect_shopify_feedback(
        self,
        *,
        keyword: str,
        market: str,
        predicted_profit: float,
        shop_domain: str | None = None,
    ) -> dict:
        orders_result = self.shopify.fetch_orders(shop_domain=shop_domain, limit=20)
        if orders_result.get("error"):
            return {
                "status": "unavailable",
                "orders": [],
                "conversion_rate": 0.0,
                "refund_rate": 0.0,
                "actual_profit": 0.0,
                "prediction_error": 0.0,
                "market_adjustment": "feedback_unavailable",
                "detail": orders_result,
            }
        orders = list(orders_result.get("orders") or [])
        revenue = sum(float(item.get("total_price") or 0) for item in orders)
        refunds = sum(float(item.get("refund_total") or 0) for item in orders)
        count = len(orders)
        conversion_rate = round(min(1.0, count / 100.0), 4)
        refund_rate = round((refunds / revenue), 4) if revenue > 0 else 0.0
        actual_profit = round(revenue - refunds, 2)
        prediction_error = round(actual_profit - float(predicted_profit or 0), 2)
        if prediction_error > 0:
            market_adjustment = "raise_opportunity_score"
        elif prediction_error < 0:
            market_adjustment = "lower_opportunity_score"
        else:
            market_adjustment = "keep_current_score"
        return {
            "status": "ok",
            "orders": orders,
            "conversion_rate": conversion_rate,
            "refund_rate": refund_rate,
            "actual_profit": actual_profit,
            "prediction_error": prediction_error,
            "market_adjustment": market_adjustment,
        }

    def record_feedback(
        self,
        db: Session,
        *,
        history_id: int | None,
        keyword: str,
        market: str,
        shop_domain: str | None,
        listing_result: str,
        predicted_profit: float,
        platform_performance: dict | None = None,
    ) -> dict:
        feedback = self.collect_shopify_feedback(
            keyword=keyword,
            market=market,
            predicted_profit=predicted_profit,
            shop_domain=shop_domain,
        )
        payload = feedback_loop_v2.record(
            decision_id=f"opportunity:{market}:{keyword}",
            keyword=keyword,
            market=market,
            listing_result=listing_result,
            publish_success_rate=1.0 if feedback["status"] == "ok" else 0.0,
            conversion_rate=float(feedback.get("conversion_rate") or 0.0),
            profit_actual=float(feedback.get("actual_profit") or 0.0),
            profit_predicted=float(predicted_profit or 0.0),
            platform_performance=platform_performance or feedback,
        )
        if history_id:
            business_opportunity_history_repository.update_actual_result(
                db,
                record_id=history_id,
                actual_result={
                    "feedback": feedback,
                    "feedback_signal": payload["feedback_signal"],
                },
                execution_result=listing_result,
                note=str(feedback.get("market_adjustment") or ""),
            )
        return {
            "feedback": feedback,
            "feedback_signal": payload["feedback_signal"],
        }


business_feedback_engine = BusinessFeedbackEngine()
