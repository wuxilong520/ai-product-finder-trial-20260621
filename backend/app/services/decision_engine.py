from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.decision import policy_engine, provider_router
from app.repositories.decision_recommendation import decision_recommendation_repository
from app.repositories.product import product_repository
from app.services.product_intelligence_engine import product_intelligence_engine
from app.services.data_hub import data_hub


class DecisionEngine:
    def recommend(self, db: Session, product_id: int, task_id: int | None = None, task_input: dict | None = None) -> dict:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise AppError("PRODUCT_NOT_FOUND", "商品不存在", "db", 404)

        policy = policy_engine.build(task_input) if task_input else None
        router = provider_router.build(policy)
        product_intelligence = product_intelligence_engine.get_or_create_intelligence(db, product_id)
        intelligence_score = float(product_intelligence["recommendation_score"])
        profit_score = float(product_intelligence["profit_score"])
        risk_score = float(product_intelligence["risk_score"])
        market_keyword = self._pick_market_keyword(product)
        market_signals = data_hub.get_market_data(db, keyword=market_keyword, task_input=task_input)
        supplier_offers = data_hub.get_supplier_data(db, keyword=market_keyword, task_input=task_input)
        cost_model = data_hub.get_cost_data(
            db=db,
            selling_price=float(product.current_price or 0),
            currency=product.currency_code or "USD",
            suppliers=supplier_offers,
            task_input=task_input,
        )
        decision = data_hub.get_decision_data(
            db,
            product_id=product_id,
            market_signals=market_signals,
            supplier_offers=supplier_offers,
            cost_model=cost_model,
            intelligence_score=intelligence_score,
            product_profit_score=profit_score,
            product_risk_score=risk_score,
            task_input=task_input,
        )

        market_score = round(float(decision.market_fit_score), 2)
        supplier_score = round(float(decision.supplier_fit_score), 2)
        final_score = round(float(decision.final_score), 2)
        recommendation, level = self._recommendation(final_score)
        reasons = list(decision.reasoning)

        payload = {
            "workspace_id": task_input.get("workspace_id") if task_input else None,
            "user_id": task_input.get("user_id") if task_input else None,
            "api_key_id": task_input.get("api_key_id") if task_input else None,
            "source_id": getattr(decision, "source_id", f"decision:{product_id}"),
            "source_type": getattr(decision, "source_type", "estimated"),
            "lineage_chain": list(getattr(decision, "lineage_chain", []) or []),
            "truth_level": getattr(decision, "truth_level", "simulated"),
            "confidence_score": round(float(getattr(decision, "confidence_score", 0.0)), 4),
            "freshness_score": round(float(getattr(decision, "freshness_score", 0.0)), 4),
            "intelligence_score": round(intelligence_score, 2),
            "market_score": market_score,
            "supplier_score": supplier_score,
            "profit_score": round(profit_score, 2),
            "risk_score": round(risk_score, 2),
            "market_fit_score": market_score,
            "supplier_fit_score": supplier_score,
            "final_score": final_score,
            "recommendation": recommendation,
            "recommendation_level": level,
            "reasons": reasons,
            "policy": policy.__dict__ if policy else {},
            "provider_routing": router.routing_metadata,
        }
        persistable_payload = {
            key: value
            for key, value in payload.items()
            if key
            in {
                "source_id",
                "source_type",
                "lineage_chain",
                "truth_level",
                "confidence_score",
                "freshness_score",
                "workspace_id",
                "user_id",
                "api_key_id",
                "intelligence_score",
                "market_score",
                "supplier_score",
                "profit_score",
                "risk_score",
                "market_fit_score",
                "supplier_fit_score",
                "final_score",
                "recommendation",
                "recommendation_level",
                "reasons",
            }
        }
        decision_recommendation_repository.upsert(db, product_id=product_id, task_id=task_id, **persistable_payload)
        return payload

    def _pick_market_keyword(self, product) -> str:
        if product.title_zh:
            return product.title_zh.split(" ")[0]
        return product.title.split(" ")[0] if product.title else f"product-{product.id}"

    def _recommendation(self, final_score: float) -> tuple[str, str]:
        if final_score >= 85:
            return "强烈推荐上架", "S"
        if final_score >= 70:
            return "推荐上架", "A"
        if final_score >= 50:
            return "继续观察", "B"
        return "不推荐", "C"


decision_engine = DecisionEngine()
