from __future__ import annotations

from sqlalchemy.orm import Session

from app.governance import lineage_writer
from app.repositories.business_truth_decision import business_truth_decision_repository
from app.repositories.decision_recommendation import decision_recommendation_repository
from app.repositories.product import product_repository
from app.services.data_hub import data_hub


class DecisionExplainService:
    def explain(
        self,
        db: Session,
        product_id: int,
        task_id: int | None = None,
        task_input: dict | None = None,
        decision_payload: dict | None = None,
        truth_payload: dict | None = None,
    ) -> dict:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            return {}

        keyword = product.title_zh or product.title or f"product-{product_id}"
        market_signals = data_hub.get_market_data(db, keyword=keyword, task_input=task_input)
        supplier_offers = data_hub.get_supplier_data(db, keyword=keyword, task_input=task_input)
        cost_model = data_hub.get_cost_data(
            db=db,
            selling_price=float(product.current_price or 0),
            currency=product.currency_code or "USD",
            suppliers=supplier_offers,
            task_input=task_input,
        )
        decision_record = (
            decision_recommendation_repository.get_by_task_id(db, task_id)
            if task_id is not None
            else decision_recommendation_repository.get_by_product_id(db, product_id)
        )
        truth_record = (
            business_truth_decision_repository.get_by_task_id(db, task_id)
            if task_id is not None
            else business_truth_decision_repository.get_by_product_id(db, product_id)
        )
        decision_json = decision_payload or getattr(decision_record, "result_json", {}) or {}
        truth_json = truth_payload or (
            {
                "truth_level": truth_record.truth_level,
                "simulated_dependencies": list(truth_record.simulated_dependencies or []),
                "lineage_chain": list(truth_record.lineage_chain or []),
                "truth_score": float(getattr(truth_record, "truth_score", 0) or 0),
            }
            if truth_record
            else {}
        )

        result = {
            "product_id": product_id,
            "task_id": task_id,
            "api_key_id": task_input.get("api_key_id") if task_input else None,
            "market_signals_used": [
                {
                    "keyword": item.keyword,
                    "source_platform": item.source_platform,
                    "trend_score": item.trend_score,
                    "demand_level": item.demand_level,
                    "competition_index": item.competition_index,
                    "confidence_score": item.confidence_score,
                    "truth_level": item.truth_level,
                }
                for item in market_signals
            ],
            "supplier_sources": [
                {
                    "supplier_name": item.supplier_name,
                    "platform": item.platform,
                    "price": item.price,
                    "match_score": item.match_score,
                    "source_type": item.source_type,
                    "truth_level": item.truth_level,
                }
                for item in supplier_offers[:5]
            ],
            "cost_breakdown": {
                "product_cost": cost_model.product_cost,
                "shipping_cost": cost_model.shipping_cost,
                "platform_fee": cost_model.platform_fee,
                "ads_cost": cost_model.ads_cost,
                "packaging_cost": cost_model.packaging_cost,
                "total_cost": cost_model.total_cost,
                "currency": cost_model.currency,
            },
            "provider_routing": dict(decision_json.get("provider_routing", {}) or {}),
            "cost_provider": getattr(cost_model, "provider_name", ""),
            "supplier_provider": supplier_offers[0].provider_name if supplier_offers else "",
            "market_provider": market_signals[0].provider_name if market_signals else "",
            "risk_factors": {
                "decision_risk_score": decision_json.get("risk_score", float(decision_record.risk_score) if decision_record else None),
                "truth_level": truth_json.get("truth_level"),
                "simulated_dependencies": list(truth_json.get("simulated_dependencies", []) or []),
            },
            "confidence_score": float(decision_json.get("confidence_score", getattr(decision_record, "confidence_score", 0.0) or 0.0)),
            "why_this_recommendation": list(decision_json.get("reasons", []) or []),
            "data_lineage": list(truth_json.get("lineage_chain", []) or decision_json.get("lineage_chain", []) or []),
            "confidence_detail": {
                "decision_confidence": float(truth_json.get("truth_score", 0) or 0),
                "cost_confidence": float(cost_model.confidence_score),
                "lineage_chain": list(truth_json.get("lineage_chain", []) or decision_json.get("lineage_chain", []) or []),
            },
        }
        lineage_writer.write_from_explain(
            db,
            result,
            task_id=task_id,
            workspace_id=task_input.get("workspace_id") if task_input else None,
            user_id=task_input.get("user_id") if task_input else None,
            source_id=(decision_json.get("source_id") if isinstance(decision_json, dict) else None) or f"decision:{product_id}",
        )
        return result


decision_explain_service = DecisionExplainService()
